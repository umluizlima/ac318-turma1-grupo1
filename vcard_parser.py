import vobject


def vcard_parser(contact):
    vcard = vobject.vCard()

    name = vcard.add('fn')
    name.value = contact['name']

    name = vcard.add('n')
    name.value = vobject.vcard.Name(family=contact['name'].split(' ')[1],
                                    given=contact['name'].split(' ')[0])

    for count, email in enumerate(contact['email']):
        e = vcard.add('email')
        e.value = email
        e.type_param = 'Internet' + str(count)

    for count, tel in enumerate(contact['tel']):
        t = vcard.add('tel')
        t.value = tel
        t.type_param = 'Tel' + str(count)

    vcard = vcard.serialize()
    vcard_file = open(contact['name'].replace(' ', '-') + '-contact.vcf', 'w')
    vcard_file.write(vcard)
    vcard_file.close()

    # return vcard


if __name__ == '__main__':
    contact = {'name': 'Teste Testus',
               'tel': ['3599814846',
                       '3534710157',
                       '05154546465'],
               'email': ['teste.testus@inatel.br',
                         'teste.testus@gmail.com.br',
                         'teste.testus@bol.com.br']}

    vcard_parser(contact)
