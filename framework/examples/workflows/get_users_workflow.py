import sys
import pathlib
import ldap
import traceback

from .ldap.ldap import LDAP


class GetUsersWorkflow():
    def __init__(self, ldap_host, ldap_username, ldap_password):
        self.conn = ldap.initialize('ldap://' + ldap_host)
        self.conn.protocol_version = 3
        self.conn.set_option(ldap.OPT_REFERRALS, 0)
        try:
            self.conn.simple_bind_s(ldap_username, ldap_password)
        except ldap.INVALID_CREDENTIALS:
            traceback.print_exc()
            raise InterruptedError
        except ldap.LDAPError:
            traceback.print_exc()
            raise InterruptedError

    def __del__(self):
        self.conn.unbind_s()

    def get_users(
        self,
        user_dn='CN=Users,DC=ad,DC=local',
        failed_counter: int = 0
    ):
        try:
            # ldap = LDAP(
            #     '192.168.6.1',
            #     'ad.local',
            #     'AD\\Administrator',
            #     'Start123!'
            # )
            # for entry in ldap.get_members(user_dn):
            #     print(entry.name)
            criteria = "(&(objectClass=*)(objectcategory=person))"
            attributes = ['displayName']
            ldap_result = self.conn.search_ext_s(
                user_dn, ldap.SCOPE_SUBTREE, criteria, attributes, sizelimit=100)
            #ldap_result = self.conn.result(ldap_result_id, 0)
            print(ldap_result)
        except Exception as e:
            traceback.print_exc()
            failed_counter = failed_counter + 1
            print('Error counter: ' + str(failed_counter))
            if failed_counter >= 5:
                return None
            attrs = {'user_dn': user_dn, 'failed_counter': failed_counter}
            return False, attrs

        return None
