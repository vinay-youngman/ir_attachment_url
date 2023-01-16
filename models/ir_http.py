# Copyright 2016-2018 Ildar Nasyrov <https://it-projects.info/team/iledarn>
# Copyright 2017 Dinar Gabbasov <https://it-projects.info/team/GabbasovDinar>
# Copyright 2016-2018,2021 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import re

import werkzeug

from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def _binary_record_content(self, record, field='datas', filename=None,
            filename_field='name', default_mimetype='application/octet-stream'):

        model = record._name

        field_def = record._fields[field]
        if field_def.type == "binary" and field_def.attachment and not field_def.related:
            if model != 'ir.attachment':
                domain = [
                    ("res_model", "=", model),
                    ("res_field", "=", field),
                    ("res_id", "=", record.id),
                    ("type", "=", "binary"),
                    ("url", "!=", False),
                ]
                field_attachment = self.env["ir.attachment"].sudo().search_read(domain=domain, fields=["url", "mimetype", "checksum"], limit=1)
                if field_attachment:
                    mimetype = field_attachment[0]["mimetype"]
                    content = field_attachment[0]["url"]
                    filehash = field_attachment[0]["checksum"]
                    return 302, content, filename, mimetype, filehash

        return super(IrHttp, self)._binary_record_content(record, field, filename, filename_field, default_mimetype)

    @classmethod
    def _binary_ir_attachment_redirect_content(
        cls, record, default_mimetype="application/octet-stream"
    ):
        if (
            record.type == "binary"
            and record.url
            and not re.match(r"^/(\w+)/(.+)$", record.url)
        ):
            mimetype = record.mimetype
            content = record.url
            filehash = record.checksum
            filename = record.name
            return 302, content, filename, mimetype, filehash
        return super(IrHttp, cls)._binary_ir_attachment_redirect_content(
            record, default_mimetype=default_mimetype
        )

    def _response_by_status(self, status, headers, content):
        if status == 302:
            return werkzeug.utils.redirect(content, code=302)
        return super(IrHttp, self)._response_by_status(status, headers, content)
