from odoo import http
from odoo.http import request


class CancelVehicleController(http.Controller):

    # [1] 외부서버로부터 수신된 데이터로 말소 등록 신청서 생성
    @http.route('/autoloadsolution/cancel/create', type='json', auth='user')
    def register_cancellation(self, **kwargs):
        """
        Required fields: owner_name, ssn, address, email, phone_number, registration_no, vehicle_id, mileage
        """
        vehicle_id = kwargs.get('vehicle_id')
        existing = request.env['autoloadsolution.cancellation'].sudo().search([
            ('vehicle_id', '=', vehicle_id)
        ], limit=1)

        if existing:
            return {
                'error': '이미 등록된 vehicle_id입니다.',
                'vehicle_id': vehicle_id
            }

        request.env['autoloadsolution.cancellation'].sudo().create(kwargs)
        return {'status': '말소등록신청서 작성 완료'}

    # [2] 말소 등록 신청서 목록 조회
    @http.route('/autoloadsolution/cancel/list', type='json', auth='user')
    def list_cancellations(self, **kwargs):
        records = request.env['autoloadsolution.cancellation'].sudo().search([
        ])
        return [{
            'owner_name': r.owner_name,
            'ssn': r.ssn,
            'address': r.address,
            'email': r.email,
            'phone_number': r.phone_number,
            'registration_no': r.registration_no,
            'vehicle_id': r.vehicle_id,
            'mileage': r.mileage,
            'status': '✔️' if r.is_checked else '❌'
        } for r in records]

    # [3] 말소 등록된 vehicle_id에 대응하여 차량 세부 정보 입력 (인보이스 생성)
    @http.route('/autoloadsolution/vehicleinfo/create', type='json', auth='user')
    def register_vehicleinfo(self, **kwargs):
        vehicle_id = kwargs.pop('vehicle_id', None)
        cancellation = request.env['autoloadsolution.cancellation'].sudo().search([
            ('vehicle_id', '=', vehicle_id)
        ], limit=1)

        if not cancellation:
            return {'error': 'vehicle_id not found'}

        # ✅ 중복 방지: 이미 해당 cancellation_id에 연결된 vehicleinfo가 존재하는지 확인
        existing_vehicleinfo = request.env['autoloadsolution.vehicleinfo'].sudo().search([
            ('cancellation_id', '=', cancellation.id)
        ], limit=1)

        if existing_vehicleinfo:
            return {'error': '이미 등록된 인보이스입니다'}

        kwargs['cancellation_id'] = cancellation.id
        request.env['autoloadsolution.vehicleinfo'].sudo().create(kwargs)
        return {'status': '말소 인보이스 작성 완료'}

    # [4] 말소 인보이스 목록 조회
    @http.route('/autoloadsolution/vehicleinfo/list', type='json', auth='user')
    def list_vehicleinfos(self, **kwargs):
        records = request.env['autoloadsolution.vehicleinfo'].sudo().search([])
        return [{
            'vehicle_id': r.cancellation_id.vehicle_id,
            'vehicle_name': r.vehicle_name,
            'vehicle_year': r.vehicle_year,
            'quantity': r.quantity,
            'unit_price': r.unit_price,
            'sales_amount': r.sales_amount,
            'vehicle_weight': r.vehicle_weight,
            'cbm': r.cbm,
        } for r in records]

    # [5] 특정 vehicle_id 기반으로 말소&선적 통합 조회
    @http.route('/autoloadsolution/search/<string:vehicle_id>', type='json', auth='user')
    def get_vehicleinfo_detail(self, vehicle_id):
        cancellation = request.env['autoloadsolution.cancellation'].sudo().search([
            ('vehicle_id', '=', vehicle_id)
        ], limit=1)
        if not cancellation:
            return {'error': 'Not found'}

        return {
            'vehicle_id': cancellation.vehicle_id,
            'owner_name': cancellation.owner_name,
            'ssn': cancellation.ssn,
            'address': cancellation.address,
            'email': cancellation.email,
            'phone_number': cancellation.phone_number,
            'registration_no': cancellation.registration_no,
            'mileage': cancellation.mileage,
            'destination': cancellation.destination,
            'invoice_date': str(cancellation.invoice_date) if cancellation.invoice_date else '',
            'is_checked': cancellation.is_checked,
            'buyer_name': cancellation.buyer_name,
            'buyer_contact': cancellation.buyer_contact,
            'vehicle_infos': [
                {
                    'vehicle_name': v.vehicle_name,
                    'vehicle_year': v.vehicle_year,
                    'quantity': v.quantity,
                    'unit_price': v.unit_price,
                    'sales_amount': v.sales_amount,
                    'vehicle_weight': v.vehicle_weight,
                    'cbm': v.cbm,
                } for v in cancellation.vehicleinfo_ids
            ]
        }


class ShippingController(http.Controller):

    # [1] 선적통관 인보이스 생성
    @http.route('/autoloadsolution/shipping/customs/create', type='json', auth='user')
    def create_customs_invoice(self, **kwargs):
        vehicle_id = kwargs.get('vehicle_id')
        destination = kwargs.get('destination')
        invoice_date = kwargs.get('invoice_date')  # YYYY-MM-DD

        cancellation = request.env['autoloadsolution.cancellation'].sudo().search([
            ('vehicle_id', '=', vehicle_id)
        ], limit=1)
        if not cancellation:
            return {'error': 'vehicle_id not found'}

        cancellation.sudo().write({
            'destination': destination,
            'invoice_date': invoice_date
        })
        return {'status': '선적통관 인보이스 작성 완료'}

    # [2] 선적통관 인보이스 조회
    @http.route('/autoloadsolution/shipping/customs/list', type='json', auth='user')
    def list_customs_invoices(self, **kwargs):
        records = request.env['autoloadsolution.cancellation'].sudo().search([
            ('destination', '!=', False),
            ('invoice_date', '!=', False)
        ])
        return [{
            'vehicle_id': r.vehicle_id,
            'destination': r.destination,
            'invoice_date': str(r.invoice_date),
            'cbm': sum(v.cbm for v in r.vehicleinfo_ids)
        } for r in records]

    # [3] 선적신청 인보이스 생성
    @http.route('/autoloadsolution/shipping/application/create', type='json', auth='user')
    def create_shipping_application_invoice(self, **kwargs):
        vehicle_id = kwargs.get('vehicle_id')
        buyer_name = kwargs.get('buyer_name')
        buyer_contact = kwargs.get('buyer_contact')

        cancellation = request.env['autoloadsolution.cancellation'].sudo().search([
            ('vehicle_id', '=', vehicle_id)
        ], limit=1)
        if not cancellation:
            return {'error': 'vehicle_id not found'}

        cancellation.sudo().write({
            'buyer_name': buyer_name,
            'buyer_contact': buyer_contact
        })
        return {'status': '선적신청 인보이스 작성 완료'}

    # [4] 선적신청 인보이스 조회
    @http.route('/autoloadsolution/shipping/application/list', type='json', auth='user')
    def list_shipping_applications(self, **kwargs):
        records = request.env['autoloadsolution.cancellation'].sudo().search([
            ('buyer_name', '!=', False),
            ('buyer_contact', '!=', False)
        ])
        return [{
            'vehicle_id': r.vehicle_id,
            'buyer_name': r.buyer_name,
            'buyer_contact': r.buyer_contact,
        } for r in records]
