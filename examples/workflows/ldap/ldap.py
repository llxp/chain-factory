from ldap3 import Server, ObjectDef, Reader
from ldap3 import NTLM, SIMPLE
from ldap3 import Connection, ALL, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES
from ldap3 import AUTO_BIND_NO_TLS, SUBTREE
from ldap3.core.exceptions import LDAPCursorError
from ldap3.core.exceptions import LDAPBindError, LDAPSocketReceiveError
from ldap3.extend.microsoft.addMembersToGroups import ad_add_members_to_groups
from ldap3.extend.microsoft.removeMembersFromGroups \
    import ad_remove_members_from_groups
from ldap3.extend.microsoft.modifyPassword import ad_modify_password


class LDAP():
    def __init__(
        self,
        server_name,
        domain_name,
        user_name,
        password,
        authentication=NTLM,
        port=389,
        use_ssl=False,
        tls=None
    ):
        self.domain_dn = self.parse_domain_name(domain_name)
        self.conn = self.connect(
            server_name,
            user_name,
            password,
            authentication,
            port,
            use_ssl,
            tls=tls
        )
        self.domain_name = domain_name
        self.bind_counter = 0

    def parse_domain_name(self, domain_name) -> str:
        """
        creates a DN from a fqdn
        e.g. domain.local ==> dc=domain,dc=local
        """
        if len(domain_name):
            splitted = domain_name.split('.')
            domain_dn = ''
            for part in splitted:
                domain_dn += ('dc=%s,' % part)
            return domain_dn[:-1]
        return ''

    def connect(
        self,
        server_name,
        user_name,
        password,
        authentication,
        port,
        use_ssl,
        tls
    ) -> Connection:
        """
        connects to the ldap or active directory server
        """
        server = Server(
            server_name,
            get_info=ALL,
            port=port,
            use_ssl=False,
            tls=tls
        )
        return Connection(
            server,
            user=user_name,
            password=password,
            authentication=authentication,
            auto_bind=True
        )

    def search(
        self,
        query,
        attributes=[ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES],
        search_base=''
    ):
        try:
            if len(search_base) <= 0:
                search_base = self.domain_dn
            if self.conn.search(search_base, query, attributes=attributes):
                return self.conn.entries
            else:
                return None
        except LDAPSocketReceiveError:
            self.bind_counter = self.bind_counter + 1
            if self.bind_counter == 10:
                return None
            self.bind()
            return self.search(query, attributes)

    def get_members(self, user_dn='CN=Users'):
        """
        performs a directory search for objects
        with the type 'person'
        and returns all results
        user_dn is the dn, where the users are stored,
        it will be prefixed to the domain dn
        """
        try:
            obj_inetorgperson = ObjectDef('person', self.conn)
            r = Reader(
                self.conn, obj_inetorgperson, user_dn + ',' + self.domain_dn)
            r.search()
            return r.entries
        except LDAPSocketReceiveError:
            self.bind_counter = self.bind_counter + 1
            if self.bind_counter == 10:
                return None
            self.bind()
            return self.get_members()

    def bind(self):
        """
        Performs an ldap bind to check, if the given credentials are valid
        """
        return self.conn.bind()

    def unbind(self):
        """
        Performs an ldap unbind to disconnect and free up resources
        """
        return self.conn.unbind()

    @staticmethod
    def authenticate(
        server_name,
        user_name,
        password,
        authentication=NTLM,
        port=389,
        use_ssl=False,
        tls=None
    ) -> bool:
        """
        checks an ldap authentication and returns True/False,
        if the authentication was successful or unsuccessful
        """
        ldap = None
        try:
            ldap = LDAP(
                server_name,
                '',
                user_name,
                password,
                authentication,
                port,
                use_ssl,
                tls
            )
            result = ldap.bind()
            ldap.conn.unbind()
            return result
        except LDAPSocketReceiveError as e:
            print('Error')
            print(e)
            return None
        except LDAPBindError:
            print('wrong credentials')
            return False

    def add_user(self, user_dn, user_name, password, email='') -> bool:
        """
        WORK IN PROGRESS
        - User Creation in disabled state: working
        - set/reset password: not working
        - enable user: not working
        """
        user_dn = 'CN=' + user_name + ',' + user_dn
        attributes = {
            'objectClass': ['organizationalPerson', 'person', 'top', 'user'],
            'sAMAccountName': user_name,
            'userPrincipalName': "{}@{}".format(user_name, self.domain_name),
            'displayName': user_name
        }
        if len(email) > 0:
            attributes['mail'] = email
        print(user_dn + ',' + self.domain_dn)
        self.conn.add(user_dn + ',' + self.domain_dn, attributes=attributes)
        if ad_modify_password(self.conn, user_dn, password, None) is False:
            print('passsword change failed')
        # self.conn.modify(
        #   user_dn, {'userAccountControl': [('MODIFY_REPLACE', 512)]})
        # self.conn.modify(
        #   user_dn, {'userAccountControl': [('MODIFY_REPLACE', 65536)]})
        return False

    def remove(self) -> bool:
        """
        Function to delete a user from active directory
        TODO: Implement
        """
        raise NotImplementedError('remove function is not yet implemented')
        return False
