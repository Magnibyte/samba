# -*- coding: utf-8 -*-
#
# Unix SMB/CIFS implementation.
# Copyright (C) Kamen Mazdrashki <kamenim@samba.org> 2010
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# Usage:
#  export SUBUNITRUN=$samba4srcdir/scripting/bin/subunitrun
#  PYTHONPATH="$PYTHONPATH:$samba4srcdir/dsdb/tests/python" $SUBUNITRUN dsdb_schema_attributes
#

import sys
import time
import random

import samba.tests
import ldb
from ldb import SCOPE_BASE, LdbError

import samba.tests

class SchemaAttributesTestCase(samba.tests.TestCase):

    def setUp(self):
        super(SchemaAttributesTestCase, self).setUp()

        self.lp = samba.tests.env_loadparm()
        self.samdb = samba.tests.connect_samdb(self.lp.samdb_url())

        # fetch rootDSE
        res = self.samdb.search(base="", expression="", scope=SCOPE_BASE, attrs=["*"])
        self.assertEquals(len(res), 1)
        self.schema_dn = res[0]["schemaNamingContext"][0]
        self.base_dn = res[0]["defaultNamingContext"][0]
        self.forest_level = int(res[0]["forestFunctionality"][0])

    def tearDown(self):
        super(SchemaAttributesTestCase, self).tearDown()

    def _ldap_schemaUpdateNow(self):
        ldif = """
dn:
changetype: modify
add: schemaUpdateNow
schemaUpdateNow: 1
"""
        self.samdb.modify_ldif(ldif)

    def _make_obj_names(self, prefix):
        obj_name = prefix + time.strftime("%s", time.gmtime())
        obj_ldap_name = obj_name.replace("-", "")
        obj_dn = "CN=%s,%s" % (obj_name, self.schema_dn)
        return (obj_name, obj_ldap_name, obj_dn)

    def _make_attr_ldif(self, attr_name, attr_dn, sub_oid, extra=None):
        ldif = """
dn: """ + attr_dn + """
objectClass: top
objectClass: attributeSchema
adminDescription: """ + attr_name + """
adminDisplayName: """ + attr_name + """
cn: """ + attr_name + """
attributeId: 1.3.6.1.4.1.7165.4.6.1.8.%d.""" % sub_oid + str(random.randint(1,100000)) + """
attributeSyntax: 2.5.5.12
omSyntax: 64
instanceType: 4
isSingleValued: TRUE
systemOnly: FALSE
"""

        if extra is not None:
            ldif += extra + "\n"

        return ldif

    def test_AddIndexedAttribute(self):
        # create names for an attribute to add
        (attr_name, attr_ldap_name, attr_dn) = self._make_obj_names("schemaAttributes-Attr-")
        ldif = self._make_attr_ldif(attr_name, attr_dn, 1,
                                    "searchFlags: %d" % samba.dsdb.SEARCH_FLAG_ATTINDEX)

        # add the new attribute
        self.samdb.add_ldif(ldif)
        self._ldap_schemaUpdateNow()

        # Check @ATTRIBUTES

        attr_res = self.samdb.search(base="@ATTRIBUTES", scope=ldb.SCOPE_BASE)

        self.assertIn(attr_ldap_name, attr_res[0])
        self.assertEquals(len(attr_res[0][attr_ldap_name]), 1)
        self.assertEquals(attr_res[0][attr_ldap_name][0], "CASE_INSENSITIVE")

        # Check @INDEXLIST

        idx_res = self.samdb.search(base="@INDEXLIST", scope=ldb.SCOPE_BASE)

        self.assertIn(attr_ldap_name, [str(x) for x in idx_res[0]["@IDXATTR"]])



    def test_AddUnIndexedAttribute(self):

        # create names for an attribute to add
        (attr_name, attr_ldap_name, attr_dn) = self._make_obj_names("schemaAttributes-Attr-")
        ldif = self._make_attr_ldif(attr_name, attr_dn, 2)

        # add the new attribute
        self.samdb.add_ldif(ldif)
        self._ldap_schemaUpdateNow()

        # Check @ATTRIBUTES

        attr_res = self.samdb.search(base="@ATTRIBUTES", scope=ldb.SCOPE_BASE)

        self.assertIn(attr_ldap_name, attr_res[0])
        self.assertEquals(len(attr_res[0][attr_ldap_name]), 1)
        self.assertEquals(attr_res[0][attr_ldap_name][0], "CASE_INSENSITIVE")

        # Check @INDEXLIST

        idx_res = self.samdb.search(base="@INDEXLIST", scope=ldb.SCOPE_BASE)

        self.assertNotIn(attr_ldap_name, [str(x) for x in idx_res[0]["@IDXATTR"]])