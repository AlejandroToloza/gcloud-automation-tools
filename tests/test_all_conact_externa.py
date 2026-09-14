from conftest import import_module_from_path

m = import_module_from_path('all_conact_externa', 'scripts/total_contacts_externals/all_conact_externa.py')


def test_obtener_contactos_pagina_hasta_total(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/externalcontacts/contacts',
        [
            {'json': {'entities': [{'id': str(i)} for i in range(100)], 'total': 150}, 'status_code': 200},
            {'json': {'entities': [{'id': str(i)} for i in range(100, 150)], 'total': 150}, 'status_code': 200},
        ],
    )

    contactos = m.obtener_contactos('token', 'api.mypurecloud.com')

    assert len(contactos) == 150
    assert requests_mock.call_count == 2


def test_obtener_contactos_vacio_no_pagina(requests_mock):
    requests_mock.get(
        'https://api.mypurecloud.com/api/v2/externalcontacts/contacts',
        json={'entities': [], 'total': 0},
    )

    contactos = m.obtener_contactos('token', 'api.mypurecloud.com')

    assert contactos == []
    assert requests_mock.call_count == 1
