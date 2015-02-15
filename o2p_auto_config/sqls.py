# -*- coding:utf-8 -*-
__author__ = 'gongxingfa'

# 根据version获取contract
get_contract_by_version = '''
select c.*
from contract c join contract_version cv on c.contract_id=cv.contract_id
where cv.version=:version
'''



# 获取baseversion的头节点描述
get_head_node_desc_list = '''
SELECT T3.VERSION BASE_VERSION,
                         T5.CON_TYPE,
                         T6.NODE_PATH,
                         T6.NODE_NAME,
                         T6.NODE_CODE,
                         T6.IS_NEED_CHECK,
                         T6.NODE_NUMBER_CONS,
                         T6.NODE_LENGTH_CONS,
                         T6.NEVL_CONS_TYPE,
                         T6.NEVL_CONS_VALUE,
                         T5.REQ_RSP,
                         T5.XSD_FORMAT,
                         T6.JAVA_FIELD
FROM CONTRACT         T1,
                         CONTRACT_VERSION T3,
                         CONTRACT_FORMAT T5,
                         NODE_DESC       T6
WHERE  T1.CONTRACT_ID = T3.CONTRACT_ID
                     AND T3.CONTRACT_VERSION_ID = T5.CONTRACT_VERSION_ID
                     AND T5.TCP_CTR_F_ID = T6.TCP_CTR_F_ID
                     AND T1.STATE = 'A'
                     AND T1.BASE_CONTRACT_ID IS NULL
                     AND T3.STATE = 'A'
                     AND T5.STATE = 'A'
                     AND T6.STATE = 'A'
                     AND T3.VERSION=:baseversion
'''

# 根据resource_alis
get_api_operation = '''
SELECT T1.RESOURCE_ALISS as resource_alis,  T1.DOC_VERSION as doc_version, T5.VERSION as version
FROM  CONTRACT_DOC     T1,
	DOC_CONTRACT     T2,
	SERVICE          T3,
	CONTRACT_VERSION T5
WHERE T1.CONTRACT_DOC_ID = T2.CONTRACT_DOC_ID
	     AND T2.CONTRACT_VERSION_ID = T3.CONTRACT_VERSION_ID
	     AND T2.CONTRACT_VERSION_ID = T5.CONTRACT_VERSION_ID
	     AND T1.DOC_TYPE = '1'
	     AND T1.RESOURCE_ALISS = :resource_alis
'''


get_contract_operation_name = '''
SELECT T1.RESOURCE_ALISS, T1.DOC_VERSION, T3.VERSION, T5.VALUE, T6.ATTR_SPEC_CODE
	  FROM CONTRACT_DOC         T1,
	       DOC_CONTRACT         T2,
	       CONTRACT_VERSION     T3,
	       CONTRACT_FORMAT      T4,
	       CONTRACT_2_ATTR_SPEC T5,
	       ATTR_SPEC            T6
	 WHERE T1.CONTRACT_DOC_ID = T2.CONTRACT_DOC_ID
	   AND T2.CONTRACT_VERSION_ID = T3.CONTRACT_VERSION_ID
	   AND T3.CONTRACT_VERSION_ID = T4.CONTRACT_VERSION_ID
	   AND T4.TCP_CTR_F_ID = T5.TCP_CTR_F_ID
	   AND T5.ATTR_SPEC_ID = T6.ATTR_SPEC_ID
 	   AND T6.ATTR_SPEC_CODE IN ('webserviceOperation','webserviceInput')
	   AND T1.DOC_TYPE = '1'
	   AND T3.VERSION = :version
	   AND T1.resource_aliss=:resource_alis
'''

# 根据base_version, resource_alis, operation用于判断是否已经配置过
if_have_configued = '''
select c.contract_id contract_id
from contract bc, contract_version bcv,
     contract c, contract_version cv,
	 contract_format cf, contract_2_attr_spec cas,
     contract_doc cd, doc_contract dc
where bc.is_base = 1
	  and bc.contract_id = c.base_contract_id
      and c.contract_id = cv.contract_id
      and cv.contract_version_id = cf.contract_version_id
      and cf.tcp_ctr_f_id = cas.TCP_CTR_F_ID
      and cd.contract_doc_id = dc.contract_doc_id
      and cv.contract_version_id = dc.contract_version_id
	  and cas.ATTR_SPEC_ID=202
      and cd.resource_aliss = :resource_alis
      and cas.value = :operation
      and cd.doc_version=:doc_version
'''