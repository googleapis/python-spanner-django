# Copyright 2020 Google LLC
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file or at
# https://developers.google.com/open-source/licenses/bsd

import os

from django.db.backends.base.features import BaseDatabaseFeatures
from django.db.utils import InterfaceError
from django_spanner import USE_EMULATOR


class DatabaseFeatures(BaseDatabaseFeatures):
    can_introspect_big_integer_field = False
    can_introspect_duration_field = False
    can_introspect_foreign_keys = False
    # TimeField is introspected as DateTimeField because they both use
    # TIMESTAMP.
    can_introspect_time_field = False
    closed_cursor_error_class = InterfaceError
    # Spanner uses REGEXP_CONTAINS which is case-sensitive.
    has_case_insensitive_like = False
    # https://cloud.google.com/spanner/quotas#query_limits
    max_query_params = 900
    if os.environ.get("RUNNING_SPANNER_BACKEND_TESTS") == "1":
        supports_foreign_keys = False
    else:
        supports_foreign_keys = True
    can_create_inline_fk = False
    supports_ignore_conflicts = False
    supports_partial_indexes = False
    supports_regex_backreferencing = False
    supports_select_for_update_with_limit = False
    supports_sequence_reset = False
    supports_timezones = False
    supports_transactions = False
    if USE_EMULATOR:
        # Emulator does not support json.
        supports_json_field = False
        # Emulator does not support check constrints.
        supports_column_check_constraints = False
        supports_table_check_constraints = False
    else:
        supports_column_check_constraints = True
        supports_table_check_constraints = True
        supports_json_field = True
    supports_primitives_in_json_field = False
    # Spanner does not support order by null modifiers.
    supports_order_by_nulls_modifier = False
    # Spanner does not support SELECTing an arbitrary expression that also
    # appears in the GROUP BY clause.
    supports_subqueries_in_group_by = False
    uses_savepoints = False
    # Spanner does not support expression indexes
    # example: CREATE INDEX index_name ON table (LOWER(column_name))
    supports_expression_indexes = False

    skip_tests = (
       "inspectdb.tests.InspectDBTestCase.test_digits_column_name_introspection",
    )

    # skip_tests = (
    #     # AssertionError: Lists differ: [<Book: Djangonaut: an art of living>, <Book: The Django Book>] != [<Book: The Django Book>, <Book: Djangonaut: an art of living>]
    #     'admin_filters.tests.ListFiltersTests.test_booleanfieldlistfilter_choices',  # noqa
    #     # AssertionError: Lists differ: [<Book: Djangonaut: an art of living>, <Book: The Django Book>] != [<Book: The Django Book>, <Book: Djangonaut: an art of living>]
    #     'admin_filters.tests.ListFiltersTests.test_booleanfieldlistfilter_tuple_choices',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Unexpected '0__c' [at 1:312]
    #     'admin_filters.tests.ListFiltersTests.test_facets_always',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Book: Djangonaut: an art of living>, <Book: Django: a biography>]
    #     'admin_filters.tests.ListFiltersTests.test_facets_filter',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Unexpected '0__c' [at 1:312]
    #     'admin_filters.tests.ListFiltersTests.test_facets_no_filter',  # noqa
    #     # AssertionError: Lists differ: [<Employee: Jack Red>, <Employee: Jane,Green>] != [<Employee: Jane,Green>, <Employee: Jack Red>]
    #     'admin_filters.tests.ListFiltersTests.test_lookup_using_custom_divider',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Book: Djangonaut: an art of living>, <B[46 chars]ook>]
    #     'admin_filters.tests.ListFiltersTests.test_multi_related_field_filter',  # noqa
    #     # AssertionError: 0 != 2
    #     'admin_filters.tests.ListFiltersTests.test_relatedfieldlistfilter_reverse_relationships',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2718666736436091352}) due to previously existing row
    #     'admin_filters.tests.ListFiltersTests.test_relatedonlyfieldlistfilter_foreignkey_default_ordering',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:800421233345595655}) due to previously existing row
    #     'admin_filters.tests.ListFiltersTests.test_relatedonlyfieldlistfilter_foreignkey_ordering',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:272112542550741833}) due to previously existing row
    #     'admin_filters.tests.ListFiltersTests.test_relatedonlyfieldlistfilter_foreignkey_reverse_relationships',  # noqa
    #     # django.db.utils.DatabaseError: Save with update_fields did not affect any rows.
    #     'admin_utils.test_logentry.LogEntryTests.test_hook_get_log_entries',  # noqa
    #     # django.db.utils.DatabaseError: Save with update_fields did not affect any rows.
    #     'admin_utils.test_logentry.LogEntryTests.test_log_action_fallback',  # noqa
    #     # django.db.utils.DatabaseError: Save with update_fields did not affect any rows.
    #     'admin_utils.test_logentry.LogEntryTests.test_log_actions',  # noqa
    #     # django.db.utils.DatabaseError: Save with update_fields did not affect any rows.
    #     'admin_utils.test_logentry.LogEntryTests.test_log_actions_single_object_param',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:4237909739519449978}) due to previously existing row
    #     'admin_utils.tests.NestedObjectsTests.test_cyclic',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:3242609140558193233}) due to previously existing row
    #     'admin_utils.tests.NestedObjectsTests.test_non_added_parent',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:4521910632409323237}) due to previously existing row
    #     'admin_utils.tests.NestedObjectsTests.test_queries',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:3883534485101983556}) due to previously existing row
    #     'admin_utils.tests.NestedObjectsTests.test_siblings',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2616225341005917343}) due to previously existing row
    #     'admin_utils.tests.NestedObjectsTests.test_unrelated_roots',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Expected end of input but got '%' [at 1:255]
    #     'custom_lookups.tests.BilateralTransformTests.test_bilateral_order',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Expected end of input but got '%' [at 1:249]
    #     'custom_lookups.tests.BilateralTransformTests.test_div3_bilateral_extract',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Type not found: CHAR [at 1:265]
    #     'custom_lookups.tests.BilateralTransformTests.test_transform_order_by',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Expected end of input but got '%' [at 1:249]
    #     'custom_lookups.tests.LookupTests.test_basic_lookup',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Syntax error: Expected end of input but got '%' [at 1:249]
    #     'custom_lookups.tests.LookupTests.test_div3_extract',  # noqa
    #     # AssertionError: Counter() != Counter({'Bugs': 1, 'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_gfk_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Bugs': 1, 'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_m2m_related_manager',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2992045494423453555}) due to previously existing row
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_default_fk_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Bugs': 1, 'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_default_gfk_related_manager',  # noqa
    #     # KeyError: 'funperson'
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_default_m2m_related_manager',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:4050303091736661446}) due to previously existing row
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_specified_fk_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_specified_gfk_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_removal_through_specified_m2m_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Bugs': 1, 'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_slow_removal_through_default_gfk_related_manager',  # noqa
    #     # AssertionError: Counter() != Counter({'Droopy': 1})
    #     'custom_managers.tests.CustomManagerTests.test_slow_removal_through_specified_gfk_related_manager',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2930240000839612056}) due to previously existing row
    #     'custom_managers.tests.CustomManagersRegressTestCase.test_filtered_default_manager',  # noqa
    #     # custom_managers.models.Book.DoesNotExist: Book matching query does not exist.
    #     'custom_managers.tests.CustomManagersRegressTestCase.test_refresh_from_db_when_default_manager_filters',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1254089530524610714}) due to previously existing row
    #     'custom_managers.tests.CustomManagersRegressTestCase.test_save_clears_annotations_from_base_manager',  # noqa
    #     # delete.models.Avatar.DoesNotExist: Avatar matching query does not exist.
    #     'delete.tests.DeletionTests.test_cannot_defer_constraint_checks',  # noqa
    #     # AssertionError: False is not true
    #     'delete.tests.DeletionTests.test_delete_with_keeping_parents',  # noqa
    #     # AssertionError: False is not true
    #     'delete.tests.DeletionTests.test_delete_with_keeping_parents_relationships',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Number of parameters in query exceeds the maximum allowed limit of 950.
    #     'delete.tests.DeletionTests.test_large_delete',  # noqa
    #     # AssertionError: <QuerySet []> is not true
    #     'delete.tests.DeletionTests.test_relational_post_delete_signals_happen_before_parent_object',  # noqa
    #     # delete.models.Avatar.DoesNotExist: Avatar matching query does not exist.
    #     'delete.tests.FastDeleteTests.test_fast_delete_fk',  # noqa
    #     # AssertionError: 0 != 1
    #     'delete.tests.FastDeleteTests.test_fast_delete_inheritance',  # noqa
    #     # AssertionError: False is not true
    #     'delete.tests.FastDeleteTests.test_fast_delete_joined_qs',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Number of parameters in query exceeds the maximum allowed limit of 950.
    #     'delete.tests.FastDeleteTests.test_fast_delete_large_batch',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'delete.tests.FastDeleteTests.test_fast_delete_qs',  # noqa
    #     # delete.models.R.DoesNotExist: R matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_cascade_from_parent',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_do_nothing',  # noqa
    #     # AttributeError: 'Base' object has no attribute 'donothing_set'
    #     'delete.tests.OnDeleteTests.test_do_nothing_qscount',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_o2o_setnull',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2319247232448674962}) due to previously existing row
    #     'delete.tests.OnDeleteTests.test_protect_path',  # noqa
    #     # AttributeError: 'DeleteTop' object has no attribute 'donothing_set'
    #     'delete.tests.OnDeleteTests.test_restrict_gfk_no_fast_delete',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2918716916701990538}) due to previously existing row
    #     'delete.tests.OnDeleteTests.test_restrict_path_cascade_direct',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2672165368701163581}) due to previously existing row
    #     'delete.tests.OnDeleteTests.test_restrict_path_cascade_indirect',  # noqa
    #     # AttributeError: 'DeleteBottom' object has no attribute 'donothing_set'
    #     'delete.tests.OnDeleteTests.test_restrict_path_cascade_indirect_diamond',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setdefault',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setdefault_none',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setnull',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setnull_from_child',  # noqa
    #     # delete.models.R.DoesNotExist: R matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setnull_from_parent',  # noqa
    #     # delete.models.A.DoesNotExist: A matching query does not exist.
    #     'delete.tests.OnDeleteTests.test_setvalue',  # noqa
    #     # AssertionError: 1 != 0
    #     'delete_regress.tests.DeleteCascadeTests.test_generic_relation_cascade',  # noqa
    #     # delete_regress.models.Researcher.DoesNotExist: Researcher matching query does not exist.
    #     'delete_regress.tests.DeleteTests.test_foreign_key_delete_nullifies_correct_columns',  # noqa
    #     # delete_regress.models.File.DoesNotExist: File matching query does not exist.
    #     'delete_regress.tests.ProxyDeleteTest.test_delete_concrete_parent',  # noqa
    #     # delete_regress.models.File.DoesNotExist: File matching query does not exist.
    #     'delete_regress.tests.ProxyDeleteTest.test_delete_proxy',  # noqa
    #     # delete_regress.models.File.DoesNotExist: File matching query does not exist.
    #     'delete_regress.tests.ProxyDeleteTest.test_delete_proxy_of_proxy',  # noqa
    #     # delete_regress.models.File.DoesNotExist: File matching query does not exist.
    #     'delete_regress.tests.ProxyDeleteTest.test_delete_proxy_pair',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'delete_regress.tests.Ticket19102Tests.test_ticket_19102_annotate',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'delete_regress.tests.Ticket19102Tests.test_ticket_19102_defer',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'delete_regress.tests.Ticket19102Tests.test_ticket_19102_extra',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'delete_regress.tests.Ticket19102Tests.test_ticket_19102_select_related',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet [4374287881601817056, 2421530947108623847, 1519325622348343236]> != [1519325622348343236, 4374287881601817056, 2421530947108623847]
    #     'expressions.tests.BasicExpressionsTests.test_nested_subquery_join_outer_ref',  # noqa
    #     # AssertionError: Lists differ: [('James Smith', 'R'), ('Jack Black', 'P'), ('Jane Doe', 'G')] != [('Jane Doe', 'G'), ('James Smith', 'R'), ('Jack Black', 'P')]
    #     'expressions_case.tests.CaseDocumentationExamples.test_conditional_update_example',  # noqa
    #     # AssertionError: Lists differ: [('Jane Doe', '5%'), ('Jack Black', '10%'), ('James Smith', '0%')] != [('Jane Doe', '5%'), ('James Smith', '0%'), ('Jack Black', '10%')]
    #     'expressions_case.tests.CaseDocumentationExamples.test_lookup_example',  # noqa
    #     # AssertionError: Lists differ: [('James Smith', '5%'), ('Jane Doe', '0%'), ('Jack Black', '10%')] != [('Jane Doe', '0%'), ('James Smith', '5%'), ('Jack Black', '10%')]
    #     'expressions_case.tests.CaseDocumentationExamples.test_simple_example',  # noqa
    #     # AssertionError: Lists differ: [(3, 'other'), (3, 'other'), (2, 'two'), (4[44 chars]ne')] != [(1, 'one'), (2, 'two'), (3, 'other'), (2, [44 chars]er')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate',  # noqa
    #     # AssertionError: Lists differ: [(2, 3, 'max'), (3, 3, 'min'), (3, 4, 'max'[57 chars]in')] != [(1, 1, 'min'), (2, 3, 'max'), (3, 4, 'max'[57 chars]in')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_aggregation_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(1, 1, ''), (3, 4, 'max = 4'), (2, 3, 'max = 3'), (3, [59 chars] 3')] != [(1, 1, ''), (2, 3, 'max = 3'), (3, 4, 'max = 4'), (2, [59 chars] '')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_aggregation_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 4, 3, 4), (4, None, 5, 5), (2, 2, 2, 3[56 chars], 1)] != [(1, None, 1, 1), (2, 2, 2, 3), (3, 4, 3, 4[56 chars], 5)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_aggregation_in_value',  # noqa
    #     # AssertionError: Lists differ: [(2, '+1'), (3, '+1'), (3, '+1'), (2, 'equa[38 chars]al')] != [(1, 'equal'), (2, '+1'), (3, '+1'), (2, 'e[38 chars]+1')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_annotation_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(3, 'one'), (2, 'zero'), (1, 'negative one[49 chars]ro')] != [(1, 'negative one'), (2, 'zero'), (3, 'one[49 chars]er')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_annotation_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (1, 2), (3, 3), (4, 4), (2, 5), (2, 5), (3, 3)] != [(1, 2), (2, 5), (3, 3), (2, 5), (3, 3), (3, 3), (4, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_annotation_in_value',  # noqa
    #     # AssertionError: Lists differ: [(3, '+1'), (1, 'equal'), (2, '+1'), (3, '+[38 chars]al')] != [(1, 'equal'), (2, '+1'), (3, '+1'), (2, 'e[38 chars]+1')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_expression_as_condition',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 5), (4, 4), (2, 5), (3, 3), (3, 3), (1, 2)] != [(1, 2), (2, 5), (3, 3), (2, 5), (3, 3), (3, 3), (4, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_expression_as_value',  # noqa
    #     # AssertionError: Lists differ: [(3, 0), (3, 0), (3, 0), (2, 0), (1, 0), (2, 0), (4, 5)] != [(1, 0), (2, 0), (3, 0), (2, 0), (3, 0), (3, 0), (4, 5)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_in_clause',  # noqa
    #     # AssertionError: Lists differ: [(1, 'equal'), (4, 'other'), (3, 'equal'), (3, '+1'), (3,[27 chars]al')] != [(1, 'equal'), (2, '+1'), (3, '+1'), (2, 'equal'), (3, '+[27 chars]er')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_join_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(4, 'one'), (3, 'three'), (3, 'three'), (2[42 chars]wo')] != [(1, 'one'), (2, 'two'), (3, 'three'), (2, [42 chars]ne')]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_join_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 5), (1, 2), (2, 5), (3, 3), (3, 3), (4, 1)] != [(1, 2), (2, 5), (3, 3), (2, 5), (3, 3), (3, 3), (4, 1)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_with_join_in_value',  # noqa
    #     # AssertionError: Lists differ: [(4, None), (3, None), (1, 1), (2, 2), (3, None), (3, None), (2, 2)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_annotate_without_default',  # noqa
    #     # AssertionError: Lists differ: [(3, 4), (2, 2), (3, 4), (2, 2), (3, 4), (4, 4), (1, 3)] != [(1, 3), (2, 2), (3, 4), (2, 2), (3, 4), (3, 4), (4, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_combined_expression',  # noqa
    #     # AssertionError: Lists differ: [(2, 2, 'when'), (1, 1, 'default'), (3, 4, [76 chars]en')] != [(1, 1, 'default'), (2, 3, 'when'), (3, 4, [76 chars]lt')]
    #     'expressions_case.tests.CaseExpressionTests.test_combined_q_object',  # noqa
    #     # AssertionError: Lists differ: [(3, 4), (3, 4), (2, 3), (1, 1)] != [(1, 1), (2, 3), (3, 4), (3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter',  # noqa
    #     # AssertionError: Lists differ: [(2, 2, 2, 3), (3, 4, 3, 4), (3, 4, 3, 4)] != [(3, 4, 3, 4), (2, 2, 2, 3), (3, 4, 3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_aggregation_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(3, 4, 4), (3, 4, 4), (2, 2, 3), (3, 3, 4), (2, 3, 3)] != [(2, 3, 3), (3, 4, 4), (2, 2, 3), (3, 4, 4), (3, 3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_aggregation_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 4, 3, 4), (3, 4, 3, 4), (2, 2, 2, 3)] != [(3, 4, 3, 4), (2, 2, 2, 3), (3, 4, 3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_aggregation_in_value',  # noqa
    #     # AssertionError: Lists differ: [(3, 4), (3, 4), (2, 2)] != [(3, 4), (2, 2), (3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_annotation_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(2, 3), (1, 1), (3, 4), (3, 4)] != [(1, 1), (2, 3), (3, 4), (3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_annotation_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 3)] != [(2, 3), (3, 3)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_annotation_in_value',  # noqa
    #     # AssertionError: Lists differ: [(3, 4, '3'), (3, 4, '3'), (2, 2, '2')] != [(3, 4, '3'), (2, 2, '2'), (3, 4, '3')]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_expression_as_condition',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 3), (1, 1)] != [(1, 1), (2, 3), (3, 3)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_expression_as_value',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 3)] != [(2, 3), (3, 3)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_join_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(1, 1), (3, 4), (3, 4), (2, 3)] != [(1, 1), (2, 3), (3, 4), (3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_join_in_predicate',  # noqa
    #     # AssertionError: Lists differ: [(3, 3), (2, 3), (1, 1)] != [(1, 1), (2, 3), (3, 3)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_with_join_in_value',  # noqa
    #     # AssertionError: Lists differ: [(3, 4), (3, 4), (2, 3)] != [(2, 3), (3, 4), (3, 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_filter_without_default',  # noqa
    #     # AssertionError: Lists differ: [(1, 1), (4, 5), (2, 2), (3, 3)] != [(1, 1), (2, 2), (3, 3), (4, 5)]
    #     'expressions_case.tests.CaseExpressionTests.test_in_subquery',  # noqa
    #     # AssertionError: Lists differ: [] != [(<CaseTestModel: CaseTestModel object (3979996847327620241)>, 3)]
    #     'expressions_case.tests.CaseExpressionTests.test_join_promotion',  # noqa
    #     # AssertionError: Lists differ: [] != [(<CaseTestModel: CaseTestModel object (1354025885826785396)>, 3, 5)]
    #     'expressions_case.tests.CaseExpressionTests.test_join_promotion_multiple_annotations',  # noqa
    #     # AssertionError: Lists differ: [(3, 3, 'default'), (3, 4, 'default'), (3, [82 chars]en')] != [(1, 1, 'default'), (2, 3, 'when'), (3, 4, [82 chars]lt')]
    #     'expressions_case.tests.CaseExpressionTests.test_lookup_different_fields',  # noqa
    #     # AssertionError: Lists differ: [(1, 'less than 2'), (4, 'greater than 2'), (2, 'equal to 2'), [82 chars] 2')] != [(1, 'less than 2'), (2, 'equal to 2'), (3, 'greater than 2'), [82 chars] 2')]
    #     'expressions_case.tests.CaseExpressionTests.test_lookup_in_condition',  # noqa
    #     # AssertionError: Lists differ: [(3, 'other'), (4, 'other'), (2, 'two'), (3[44 chars]er')] != [(1, 'one'), (2, 'two'), (3, 'other'), (2, [44 chars]er')]
    #     'expressions_case.tests.CaseExpressionTests.test_update',  # noqa
    #     # AssertionError: Lists differ: [(2, 2), (1, 1), (3, None), (2, 2), (4, None), (3, None), (3, None)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_big_integer',  # noqa
    #     # AssertionError: Lists differ: [(3, b''), (3, b''), (4, b''), (1, b'one'), (3, b''), (2, b'two'), (2, b'two')] != [(1, b'one'), (2, b'two'), (3, b''), (2, b'two'), (3, b''), (3, b''), (4, b'')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_binary',  # noqa
    #     # AssertionError: Lists differ: [(1, [13 chars]ue), (4, False), (3, False), (2, True), (3, False), (3, False)] != [(1, [13 chars]ue), (3, False), (2, True), (3, False), (3, False), (4, False)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_boolean',  # noqa
    #     # AssertionError: Lists differ: [(3, None), (2, datetime.date(2015, 1, 2)),[92 chars]one)] != [(1, datetime.date(2015, 1, 1)), (2, dateti[92 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_date',  # noqa
    #     # AssertionError: Lists differ: [(2, datetime.datetime(2015, 1, 2, 0, 0)), [122 chars]one)] != [(1, datetime.datetime(2015, 1, 1, 0, 0)), [122 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_date_time',  # noqa
    #     # AssertionError: Lists differ: [(3, None), (1, datetime.timedelta(days=1))[95 chars]=2))] != [(1, datetime.timedelta(days=1)), (2, datet[95 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_duration',  # noqa
    #     # AssertionError: Lists differ: [(3, ''), (3, ''), (3, ''), (2, '2@example.[54 chars]om')] != [(1, '1@example.com'), (2, '2@example.com')[54 chars] '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_email',  # noqa
    #     # AssertionError: Lists differ: [(2, '~/2'), (1, '~/1'), (3, ''), (3, ''), (3, ''), (4, ''), (2, '~/2')] != [(1, '~/1'), (2, '~/2'), (3, ''), (2, '~/2'), (3, ''), (3, ''), (4, '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_file',  # noqa
    #     # AssertionError: Lists differ: [(2, '~/2'), (4, ''), (3, ''), (3, ''), (3, ''), (2, '~/2'), (1, '~/1')] != [(1, '~/1'), (2, '~/2'), (3, ''), (2, '~/2'), (3, ''), (3, ''), (4, '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_file_path',  # noqa
    #     # AssertionError: Lists differ: [(4, None), (3, None), (1, 1367412237981814[72 chars]434)] != [(1, 1367412237981814818), (2, 585835158945[72 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_fk',  # noqa
    #     # google.api_core.exceptions.InvalidArgument: 400 Could not parse number_value: 1.1
    #     'expressions_case.tests.CaseExpressionTests.test_update_float',  # noqa
    #     # AssertionError: Lists differ: [(3, None), (4, None), (3, None), (2, '2.2.[44 chars].2')] != [(1, '1.1.1.1'), (2, '2.2.2.2'), (3, None),[44 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_generic_ip_address',  # noqa
    #     # AssertionError: Lists differ: [(3, None), (2, False), (3, None), (1, True), (2, False), (3, None), (4, None)] != [(1, True), (2, False), (3, None), (2, False), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_null_boolean',  # noqa
    #     # AssertionError: Lists differ: [(2, 2), (3, None), (2, 2), (3, None), (1, 1), (4, None), (3, None)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_positive_big_integer',  # noqa
    #     # AssertionError: Lists differ: [(2, 2), (2, 2), (1, 1), (4, None), (3, None), (3, None), (3, None)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_positive_integer',  # noqa
    #     # AssertionError: Lists differ: [(1, 1), (3, None), (3, None), (2, 2), (2, 2), (4, None), (3, None)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_positive_small_integer',  # noqa
    #     # AssertionError: Lists differ: [(2, '2'), (3, ''), (4, ''), (1, '1'), (2, '2'), (3, ''), (3, '')] != [(1, '1'), (2, '2'), (3, ''), (2, '2'), (3, ''), (3, ''), (4, '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_slug',  # noqa
    #     # AssertionError: Lists differ: [(2, 2), (3, None), (2, 2), (3, None), (4, None), (1, 1), (3, None)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_small_integer',  # noqa
    #     # AssertionError: Lists differ: [(2, '2'), (2, '2'), (1, '1')] != [(1, '1'), (2, '2'), (2, '2')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_string',  # noqa
    #     # AssertionError: Lists differ: [(4, ''), (2, '2'), (3, ''), (2, '2'), (1, '1'), (3, ''), (3, '')] != [(1, '1'), (2, '2'), (3, ''), (2, '2'), (3, ''), (3, ''), (4, '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_text',  # noqa
    #     # AssertionError: Lists differ: [(1, [54 chars]ne), (3, None), (3, None), (2, datetime.time(2, 0)), (4, None)] != [(1, [54 chars]ne), (2, datetime.time(2, 0)), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_time',  # noqa
    #     # AssertionError: Lists differ: [(2, 'http://2.example.com/'), (2, 'http://[78 chars] '')] != [(1, 'http://1.example.com/'), (2, 'http://[78 chars] '')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_url',  # noqa
    #     # AssertionError: Lists differ: [(2, UUID('22222222-2222-2222-2222-22222222[149 chars]one)] != [(1, UUID('11111111-1111-1111-1111-11111111[149 chars]one)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_uuid',  # noqa
    #     # AssertionError: Lists differ: [(1, 'equal'), (3, '+1'), (4, '+1'), (3, 'equal'), (2, '+[24 chars]+1')] != [(1, 'equal'), (2, '+1'), (3, '+1'), (2, 'equal'), (3, '+[24 chars]+1')]
    #     'expressions_case.tests.CaseExpressionTests.test_update_with_expression_as_condition',  # noqa
    #     # AssertionError: Lists differ: [('4', 4), ('3', 3), ('1', 2), ('3', 3), ('2', 5), ('3', 3), ('2', 5)] != [('1', 2), ('2', 5), ('3', 3), ('2', 5), ('3', 3), ('3', 3), ('4', 4)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_with_expression_as_value',  # noqa
    #     # AssertionError: Lists differ: [(3, None), (2, 2), (4, None), (3, None), (2, 2), (3, None), (1, 1)] != [(1, 1), (2, 2), (3, None), (2, 2), (3, None), (3, None), (4, None)]
    #     'expressions_case.tests.CaseExpressionTests.test_update_without_default',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:698553405026791122}) due to previously existing row
    #     'extra_regress.tests.ExtraRegressTests.test_dates_query',  # noqa
    #     # AssertionError: Lists differ: [] != [{'alpha': 5, 'beta': 4, 'gamma': 3}]
    #     'extra_regress.tests.ExtraRegressTests.test_extra_stay_tied',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<TestObject: TestObject: first,second,third>]
    #     'extra_regress.tests.ExtraRegressTests.test_regression_10847',  # noqa
    #     # AssertionError: Lists differ: [] != [2209773301735979797]
    #     'extra_regress.tests.ExtraRegressTests.test_regression_7961',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<User: fred>]
    #     'extra_regress.tests.ExtraRegressTests.test_regression_8819',  # noqa
    #     # filtered_relation.models.Book.DoesNotExist: Book matching query does not exist.
    #     'filtered_relation.tests.FilteredRelationTests.test_defer',  # noqa
    #     # AssertionError: Lists differ: [(<Au[16 chars]ect (236906812684237367)>, <Editor: Editor obj[212 chars]4)>)] != [(<Au[16 chars]ect (3012576906549871166)>, <Editor: Editor ob[212 chars]0)>)]
    #     'filtered_relation.tests.FilteredRelationTests.test_nested_foreign_key',  # noqa
    #     # AssertionError: Lists differ: [(<Au[16 chars]ect (3161094245469267643)>, <Book: Book object[670 chars]6)>)] != [(<Au[16 chars]ect (4081081433700392266)>, <Book: Book object[670 chars]3)>)]
    #     'filtered_relation.tests.FilteredRelationTests.test_select_related',  # noqa
    #     # AssertionError: Lists differ: [(<Bo[104 chars]ect (3651164148391812823)>, <Author: Author ob[208 chars]1)>)] != [(<Bo[104 chars]ect (4422084702129245401)>, <Author: Author ob[208 chars]7)>)]
    #     'filtered_relation.tests.FilteredRelationTests.test_select_related_foreign_key',  # noqa
    #     # AssertionError: Lists differ: [(<Book: Book object (639667689057585893)>, <Author: Author obj[485 chars]4)>)] != [(<Book: Book object (2841054760192094425)>, <Author: Author ob[485 chars]4)>)]
    #     'filtered_relation.tests.FilteredRelationTests.test_select_related_multiple',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:877463916671332695}) due to previously existing row
    #     'fixtures.tests.CircularReferenceTests.test_circular_reference_natural_key',  # noqa
    #     # KeyError: 'content_type'
    #     'fixtures.tests.FixtureLoadingTests.test_dumpdata_objects_with_prefetch_related',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:877463916671332695}) due to previously existing row
    #     'fixtures.tests.FixtureLoadingTests.test_loaddata_app_option',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:877463916671332695}) due to previously existing row
    #     'fixtures.tests.FixtureLoadingTests.test_unmatched_identifier_loading',  # noqa
    #     # AssertionError: Element counts were not equal:
    #     'fixtures_regress.tests.M2MNaturalKeyFixtureTests.test_dump_and_load_m2m_simple',  # noqa
    #     # KeyError: 'author'
    #     'fixtures_regress.tests.NaturalKeyFixtureOnOtherDatabaseTests.test_natural_key_dependencies',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_fallback_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_post_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_post_unknown_page',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_post_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_csrf.FlatpageCSRFTests.test_view_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_admin_form_edit',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_admin_form_url_uniqueness_validation',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_admin_form_url_validation',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_doesnt_requires_trailing_slash_without_append_slash',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_nosites',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_requires_leading_slash',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_forms.FlatpageAdminFormTests.test_flatpage_requires_trailing_slash_with_append_slash',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_fallback_flatpage_root',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_fallback_flatpage_special_chars',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_fallback_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareAppendSlashTests.test_redirect_view_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_fallback_flatpage_special_chars',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_fallback_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_view_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_sitemaps.FlatpagesSitemapTests.test_flatpage_sitemap',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_tag',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_tag_for_anon_user',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_with_prefix',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_with_prefix_for_anon_user',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_with_variable_prefix',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_parsing_errors',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewAppendSlashTests.test_redirect_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewAppendSlashTests.test_redirect_fallback_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewAppendSlashTests.test_redirect_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewAppendSlashTests.test_redirect_view_flatpage_special_chars',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewAppendSlashTests.test_redirect_view_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewTests.test_fallback_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewTests.test_fallback_non_existent_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewTests.test_view_flatpage',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewTests.test_view_flatpage_special_chars',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1}) due to previously existing row
    #     'flatpages_tests.test_views.FlatpageViewTests.test_view_non_existent_flatpage',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_aware_datetime_date_detail',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_date_detail_allow_future',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_date_detail_by_pk',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_date_detail_custom_month_format',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_datetime_date_detail',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_dates.DateDetailViewTests.test_get_object_custom_queryset',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1219012950021730710}) due to previously existing row
    #     'generic_views.test_dates.DayArchiveViewTests.test_aware_datetime_day_view',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_context_object_name',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_custom_detail',  # noqa
    #     # generic_views.models.Author.DoesNotExist: Author matching query does not exist.
    #     'generic_views.test_detail.DetailViewTest.test_deferred_queryset_context_object_name',  # noqa
    #     # generic_views.models.Author.DoesNotExist: Author matching query does not exist.
    #     'generic_views.test_detail.DetailViewTest.test_deferred_queryset_template_name',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_detail_by_custom_pk',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_detail_by_pk',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_detail_by_pk_and_slug',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_detail_by_pk_ignore_slug',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_detail_by_pk_ignore_slug_mismatch',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_duplicated_context_object_name',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_template_name',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_template_name_field',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_template_name_suffix',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_detail.DetailViewTest.test_verbose_name',  # noqa
    #     # AssertionError: 404 != 200 : Couldn't retrieve redirection page '/edit/author/859460047870351588/update/': response code was 404 (expected 200)
    #     'generic_views.test_edit.CreateViewTests.test_create_with_interpolated_redirect',  # noqa
    #     # AssertionError: 404 != 200 : Couldn't retrieve redirection page '/detail/artist/226157415023904884/': response code was 404 (expected 200)
    #     'generic_views.test_edit.CreateViewTests.test_create_with_object_url',  # noqa
    #     # AssertionError: 404 != 200 : Couldn't retrieve redirection page '/detail/author/3458255619212185607/': response code was 404 (expected 200)
    #     'generic_views.test_edit.CreateViewTests.test_create_with_special_properties',  # noqa
    #     # AssertionError: 404 != 302
    #     'generic_views.test_edit.DeleteViewTests.test_delete_by_delete',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_edit.DeleteViewTests.test_delete_by_post',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_edit.DeleteViewTests.test_delete_with_form_as_post',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_edit.DeleteViewTests.test_delete_with_form_as_post_with_validation_error',  # noqa
    #     # AssertionError: 404 != 302
    #     'generic_views.test_edit.DeleteViewTests.test_delete_with_interpolated_redirect',  # noqa
    #     # AssertionError: 404 != 302
    #     'generic_views.test_edit.DeleteViewTests.test_delete_with_redirect',  # noqa
    #     # AssertionError: 404 != 200
    #     'generic_views.test_edit.DeleteViewTests.test_delete_with_special_properties',  # noqa
    #     # AssertionError: ImproperlyConfigured not raised
    #     'generic_views.test_edit.DeleteViewTests.test_delete_without_redirect',  # noqa
    #     # AssertionError: 404 != 302
    #     'generic_views.test_edit.UpdateViewTests.test_update_with_object_url',  # noqa
    #     # known_related_objects.models.Tournament.DoesNotExist: Tournament matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_foreign_key',  # noqa
    #     # known_related_objects.models.Tournament.DoesNotExist: Tournament matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_foreign_key_prefetch_related',  # noqa
    #     # KeyError: 'pool'
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_multilevel_reverse_fk_cyclic_select_related',  # noqa
    #     # known_related_objects.models.PoolStyle.DoesNotExist: PoolStyle matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one',  # noqa
    #     # known_related_objects.models.PoolStyle.DoesNotExist: PoolStyle matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_prefetch_related',  # noqa
    #     # known_related_objects.models.PoolStyle.DoesNotExist: PoolStyle matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_one_to_one_select_related',  # noqa
    #     # IndexError: list index out of range
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_and',  # noqa
    #     # IndexError: list index out of range
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_or_different_cached_items',  # noqa
    #     # AssertionError: Items in the second set but not the first:
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_queryset_or_only_one_with_precache',  # noqa
    #     # known_related_objects.models.Pool.DoesNotExist: Pool matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one',  # noqa
    #     # known_related_objects.models.Pool.DoesNotExist: Pool matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_prefetch_related',  # noqa
    #     # known_related_objects.models.Pool.DoesNotExist: Pool matching query does not exist.
    #     'known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_select_related',  # noqa
    #     # AssertionError: Lists differ: [{'in[449 chars]'pre_add', 'reverse': False, 'model': <class '[445 chars])>]}] != [{'in[449 chars]'pre_remove', 'reverse': False, 'model': <clas[840 chars])>]}]
    #     'm2m_signals.tests.ManyToManySignalsTest.test_m2m_relations_signals_alternative_ways',  # noqa
    #     # AssertionError: Lists differ: [{'in[900 chars]'pre_add', 'reverse': False, 'model': <class '[161 chars]t'>}] != [{'in[900 chars]'pre_remove', 'reverse': False, 'model': <clas[277 chars])>]}]
    #     'm2m_signals.tests.ManyToManySignalsTest.test_m2m_relations_signals_clearing_removing',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<PersonSelfRefM2M: PersonSelfRefM2M object (1221558887748430855)>]
    #     'm2m_through.tests.M2mThroughReferentialTests.test_add_on_symmetrical_m2m_with_intermediate_model',  # noqa
    #     # AssertionError: Lists differ: [] != ['Chris']
    #     'm2m_through.tests.M2mThroughReferentialTests.test_self_referential_non_symmetrical_both',  # noqa
    #     # AssertionError: Lists differ: [] != ['Chris']
    #     'm2m_through.tests.M2mThroughReferentialTests.test_self_referential_non_symmetrical_clear_first_side',  # noqa
    #     # AssertionError: Lists differ: [] != ['Chris']
    #     'm2m_through.tests.M2mThroughReferentialTests.test_self_referential_non_symmetrical_first_side',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<PersonSelfRefM2M: PersonSelfRefM2M object (1542819018270698516)>]
    #     'm2m_through.tests.M2mThroughReferentialTests.test_self_referential_symmetrical',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<PersonSelfRefM2M: PersonSelfRefM2M obje[87 chars]59)>]
    #     'm2m_through.tests.M2mThroughReferentialTests.test_set_on_symmetrical_m2m_with_intermediate_model',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (2582787503822711123)>]
    #     'm2m_through.tests.M2mThroughTests.test_add_on_m2m_with_intermediate_model',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (3266042330056946[48 chars]61)>]
    #     'm2m_through.tests.M2mThroughTests.test_add_on_m2m_with_intermediate_model_callable_through_default',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (1800310795732488898)>]
    #     'm2m_through.tests.M2mThroughTests.test_create_on_m2m_with_intermediate_model',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (2790206054983804420)>]
    #     'm2m_through.tests.M2mThroughTests.test_create_on_m2m_with_intermediate_model_callable_through_default',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (2254829871517973[48 chars]54)>]
    #     'm2m_through.tests.M2mThroughTests.test_remove_on_m2m_with_intermediate_model_multiple',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Person: Person object (4507451925922924[48 chars]74)>]
    #     'm2m_through.tests.M2mThroughTests.test_set_on_m2m_with_intermediate_model_callable_through_default',  # noqa
    #     # AssertionError: Lists differ: [] != ['Jane', 'Jim']
    #     'm2m_through.tests.M2mThroughTests.test_through_fields',  # noqa
    #     # AssertionError: Element counts were not equal:
    #     'm2m_through_regress.test_multitable.MultiTableTests.test_m2m_query',  # noqa
    #     # AssertionError: Element counts were not equal:
    #     'm2m_through_regress.test_multitable.MultiTableTests.test_m2m_query_proxied',  # noqa
    #     # AssertionError: Element counts were not equal:
    #     'm2m_through_regress.test_multitable.MultiTableTests.test_m2m_reverse_query',  # noqa
    #     # AssertionError: Element counts were not equal:
    #     'm2m_through_regress.test_multitable.MultiTableTests.test_m2m_reverse_query_proxied',  # noqa
    #     # AssertionError: Lists differ: [('mi[49 chars] '0002_second'), ('migrations2', '0001_squashe[37 chars]al')] != [('mi[49 chars] '0001_initial'), ('migrations2', '0002_second[37 chars]02')]
    #     'migrations.test_commands.MigrateTests.test_prune_respect_app_label',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_custom_user',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_detect_soft_applied_add_field_manytomanyfield',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_empty_plan',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrate_backward_to_squashed_migration',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrate_marks_replacement_applied_even_if_it_did_nothing',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrate_marks_replacement_unapplied',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrate_skips_schema_creation',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrations_applied_and_recorded_atomically',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_migrations_not_applied_on_deferred_sql_failure',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_mixed_plan_not_supported',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_non_atomic_migration',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_process_callback',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_run',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_run_with_squashed',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_unrelated_applied_migrations_mutate_state',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_unrelated_model_lookups_backwards',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: django_content_type.id in table: django_content_type
    #     'migrations.test_executor.ExecutorTests.test_unrelated_model_lookups_forwards',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: test_mltdb_runsql3_pony.id in table: test_mltdb_runsql3_pony
    #     'migrations.test_multidb.MultiDBOperationTests.test_run_sql_migrate_foo_router_with_hints',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 A new row in table test_adflbddd_pony does not specify a non-null value for NOT NULL column: height
    #     'migrations.test_operations.OperationTests.test_add_field_both_defaults',  # noqa
    #     # AssertionError: None != 4
    #     'migrations.test_operations.OperationTests.test_add_field_database_default',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: height in table: test_adflddf_pony referenced by key: {Int64(364560731518364946)} 9: Cannot specify a null...
    #     'migrations.test_operations.OperationTests.test_add_field_database_default_function',  # noqa
    #     # AssertionError: 'special_char' unexpectedly found in ['id', 'pink', 'weight', 'green', 'yellow', 'special_char']
    #     'migrations.test_operations.OperationTests.test_add_field_database_default_special_char_escaping',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alterconstraint_pony with indices: test_alter_constraint_pony_fields_uq.
    #     'migrations.test_operations.OperationTests.test_alter_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alterconstraint_pony with indices: test_alter_constraint_pony_fields_uq.
    #     'migrations.test_operations.OperationTests.test_alter_field_add_database_default',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alterconstraint_pony with indices: test_alter_constraint_pony_fields_uq.
    #     'migrations.test_operations.OperationTests.test_alter_field_add_db_column_noop',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_change_blank_nullable_database_default_to_not_null',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_change_default_to_database_default',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_change_nullable_to_database_default_not_null',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_change_nullable_to_decimal_database_default_not_null',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_foreignobject_noop',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_pk_fk_db_collation',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_afadbn_rider with indices: test_afadbn_rider_pony_id_d47f6ec5,test_afadbn_rider_friend_id_f355bd15.
    #     'migrations.test_operations.OperationTests.test_alter_field_pk_mti_and_fk_to_base',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_field_pk_mti_fk',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_field_reloads_state_fk_with_to_field_related_name_target_type_change',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_type_change',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_field_with_func_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_id_pk_to_uuid_pk',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_index_together_remove_with_unique_together',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_alter_model_table_comment',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_autofield__bigautofield_foreignfield_growth',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_composite_pk_operations',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_create_fk_models_to_pk_field_db_collation',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_create_model_constraint_percent_escaping',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_create_model_with_boolean_expression_in_check_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_create_model_with_covering_unique_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_generated_field_changes_output_field',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_invalid_generated_field_changes_on_rename_stored',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_invalid_generated_field_changes_on_rename_virtual',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_invalid_generated_field_changes_stored',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_invalid_generated_field_changes_virtual',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_invalid_generated_field_persistency_change',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_covering_unique_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_deferred_unique_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_func_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_func_unique_constraint',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_generated_field_stored',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_generated_field_virtual',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_remove_unique_together_on_pk_field',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_rename_field_add_non_nullable_field_with_composite_pk',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rfwdbc_pony with indices: test_rfwdbc_pony_db_fk_field_005950bb.
    #     'migrations.test_operations.OperationTests.test_rename_field_with_db_column',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_rename_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_rename_index_arguments',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_rename_index_state_forwards',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_alflpkmtifk_shetlandrider with indices: test_alflpkmtifk_shetlandrider_pony_id_66e71f92.
    #     'migrations.test_operations.OperationTests.test_rename_index_state_forwards_unnamed_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_index_unknown_unnamed_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_index_unnamed_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_index_unnamed_index_with_unique_index',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_m2m_field_with_2_references',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_model_no_relations_with_db_table_noop',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_rename_model_with_db_table_and_fk_noop',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_run_python_invalid_reverse_code',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_run_sql_add_missing_semicolon_on_collect_sql',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_run_sql_backward_reverse_sql_required',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_smallfield_autofield_foreignfield_growth',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot drop table test_rnidsfui_pony with indices: test_rnidsfui_pony_weight_pink_49fa4b8b_idx.
    #     'migrations.test_operations.OperationTests.test_smallfield_bigautofield_foreignfield_growth',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1485591505974932196}) due to previously existing row
    #     'model_forms.tests.FileAndImageFieldTests.test_file_field_data',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2460314589753408882}) due to previously existing row
    #     'model_forms.tests.FileAndImageFieldTests.test_filefield_required_false',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:3935244914170661535}) due to previously existing row
    #     'model_forms.tests.ModelFormBaseTest.test_blank_false_with_null_true_foreign_key_field',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.ModelFormBaseTest.test_blank_with_null_foreign_key_field',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:877367358247552621}) due to previously existing row
    #     'model_forms.tests.ModelFormBaseTest.test_save_blank_false_with_required_false',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:2476540305045542110}) due to previously existing row
    #     'model_forms.tests.ModelFormBasicTests.test_custom_form_fields',  # noqa
    #     # ValueError: The Article could not be created because the data didn't validate.
    #     'model_forms.tests.ModelFormBasicTests.test_m2m_editing',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: model_forms_article.created in table: model_forms_article
    #     'model_forms.tests.ModelFormBasicTests.test_subset_fields',  # noqa
    #     # AssertionError: False is not True
    #     'model_forms.tests.ModelFormBasicTests.test_validate_foreign_key_to_model_with_overridden_manager',  # noqa
    #     # google.api_core.exceptions.FailedPrecondition: 400 Cannot specify a null value for column: model_forms_article.created in table: model_forms_article
    #     'model_forms.tests.ModelMultipleChoiceFieldTests.test_to_field_name_with_initial_data',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1028010144685281847}) due to previously existing row
    #     'model_forms.tests.ModelOneToOneFieldTests.test_assignment_of_none',  # noqa
    #     # ValueError: The WriterProfile could not be created because the data didn't validate.
    #     'model_forms.tests.ModelOneToOneFieldTests.test_onetoonefield',  # noqa
    #     # AssertionError: Lists differ: [] != [<Colour: blue>]
    #     'model_forms.tests.ModelToDictTests.test_many_to_many',  # noqa
    #     # ValueError: The Inventory could not be changed because the data didn't validate.
    #     'model_forms.tests.OtherModelFormTests.test_foreignkeys_which_use_to_field',  # noqa
    #     # AssertionError: 2 != 1
    #     'model_forms.tests.UniqueTest.test_abstract_inherited_unique',  # noqa
    #     # AssertionError: 2 != 1
    #     'model_forms.tests.UniqueTest.test_abstract_inherited_unique_together',  # noqa
    #     # AssertionError: 2 != 1
    #     'model_forms.tests.UniqueTest.test_inherited_unique',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.UniqueTest.test_inherited_unique_for_date',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.UniqueTest.test_inherited_unique_together',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.UniqueTest.test_simple_unique',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.UniqueTest.test_unique_for_date',  # noqa
    #     # AssertionError: False is not true
    #     'model_forms.tests.UniqueTest.test_unique_null',  # noqa
    #     # AssertionError: False is not true
    #     'model_formsets.tests.DeletionTests.test_outdated_deletion',  # noqa
    #     # AssertionError: False is not true
    #     'model_formsets.tests.ModelFormsetTest.test_commit_false',  # noqa
    #     # AssertionError: False is not True
    #     'model_formsets.tests.ModelFormsetTest.test_edit_only',  # noqa
    #     # AssertionError: False is not True
    #     'model_formsets.tests.ModelFormsetTest.test_edit_only_formset_factory_with_basemodelformset',  # noqa
    #     # AssertionError: False is not True
    #     'model_formsets.tests.ModelFormsetTest.test_edit_only_inlineformset_factory',  # noqa
    #     # AssertionError: False is not true
    #     'model_formsets.tests.ModelFormsetTest.test_inline_formsets',  # noqa
    #     # KeyError: 'team'
    #     'model_formsets.tests.ModelFormsetTest.test_inlineformset_factory_with_null_fk',  # noqa
    #     # AssertionError: False is not true
    #     'model_formsets.tests.ModelFormsetTest.test_model_inheritance',  # noqa
    #     # AssertionError: False is not true
    #     'model_formsets.tests.ModelFormsetTest.test_simple_save',  # noqa
    #     # AssertionError: Errors found on formset:[{'id': ['Select a valid choice. That choice is not one of the available choices.']}]
    #     'model_formsets_regress.tests.InlineFormsetTests.test_formset_over_inherited_model',  # noqa
    #     # AssertionError: Errors found on formset:[{'id': ['Select a valid choice. That choice is not one of the available choices.']}]
    #     'model_formsets_regress.tests.InlineFormsetTests.test_formset_over_to_field',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet [<Parent: Parent object (138329[58 chars]0)>]> != [<Parent: Parent object (2878855750519726[47 chars]30)>]
    #     'model_inheritance.tests.ModelInheritanceTests.test_inherited_ordering_pk_desc',  # noqa
    #     # AssertionError: Lists differ: [] != [<BirthdayParty: BirthdayParty object (2574610211792724733)>]
    #     'model_inheritance_regress.tests.ModelInheritanceTest.test_abstract_base_class_m2m_relation_inheritance',  # noqa
    #     # model_inheritance_regress.models.User.DoesNotExist: User matching query does not exist.
    #     'model_inheritance_regress.tests.ModelInheritanceTest.test_create_new_instance_with_pk_equals_none',  # noqa
    #     # model_inheritance_regress.models.Person.DoesNotExist: Person matching query does not exist.
    #     'model_inheritance_regress.tests.ModelInheritanceTest.test_create_new_instance_with_pk_equals_none_multi_inheritance',  # noqa
    #     # AssertionError: False is not true
    #     'model_inheritance_regress.tests.ModelInheritanceTest.test_inherited_unique_field_with_form',  # noqa
    #     # model_inheritance_regress.models.Place.DoesNotExist: Place matching query does not exist.
    #     'model_inheritance_regress.tests.ModelInheritanceTest.test_issue_7276',  # noqa
    #     # AssertionError: Lists differ: [] != [1]
    #     'model_regress.tests.ModelTests.test_date_filter_null',  # noqa
    #     # model_regress.models.Article.DoesNotExist: Article matching query does not exist.
    #     'model_regress.tests.ModelTests.test_empty_choice',  # noqa
    #     # AssertionError: datetime.datetime(2000, 1, 1, 12, 0, 20, 24) != datetime.datetime(2000, 1, 1, 6, 1, 1)
    #     'model_regress.tests.ModelTests.test_get_next_prev_by_field',  # noqa
    #     # model_regress.models.Article.DoesNotExist: Article matching query does not exist.
    #     'model_regress.tests.ModelTests.test_long_textfield',  # noqa
    #     # model_regress.models.Article.DoesNotExist: Article matching query does not exist.
    #     'model_regress.tests.ModelTests.test_long_unicode_textfield',  # noqa
    #     # AssertionError: Lists differ: [] != ['custom_action']
    #     'modeladmin.test_actions.AdminActionsTests.test_get_actions_respects_permissions',  # noqa
    #     # KeyError: 'content_type'
    #     'modeladmin.tests.ModelAdminTests.test_log_actions',  # noqa
    #     # KeyError: 'content_type'
    #     'modeladmin.tests.ModelAdminTests.test_log_deletion',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet [(3505535116110580797, 12682459[236 chars]'')]> != [(3505535116110580797, 126824595474708279[225 chars] '')]
    #     'modeladmin.tests.ModelAdminTests.test_log_deletion_fallback',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet [(2787430962434337855, 66691067[232 chars]'')]> != [(2787430962434337855, 666910670159521668[221 chars] '')]
    #     'modeladmin.tests.ModelAdminTests.test_log_deletions',  # noqa
    #     # django.core.exceptions.ValidationError: {'owner': ['person instance with id 1164865903192662971 is not a valid choice.']}
    #     'multiple_database.tests.QueryTestCase.test_foreign_key_validation',  # noqa
    #     # django.core.exceptions.ValidationError: ['person instance with id 1742199134075767842 is not a valid choice.']
    #     'multiple_database.tests.QueryTestCase.test_foreign_key_validation_with_router',  # noqa
    #     # multiple_database.models.Book.DoesNotExist: Book matching query does not exist.
    #     'multiple_database.tests.RouterTestCase.test_deferred_models',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:3360412713858443898}) due to previously existing row
    #     'multiple_database.tests.SignalTests.test_database_arg_save_and_delete',  # noqa
    #     # AssertionError: Lists differ: [<Scr[54 chars]003)>, <ScreeningNullFK: ScreeningNullFK objec[20 chars]84)>] != [<Scr[54 chars]003)>]
    #     'nested_foreign_keys.tests.NestedForeignKeysTests.test_null_exclude',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:169157739193595396}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_assign_none_reverse_relation',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1756083816253810606}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_assign_o2o_id_none',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1500036199283904459}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_assign_o2o_id_value',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1432148271646272397}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_cached_relation_invalidated_on_save',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Restaurant: Demon Dogs the restaurant>]
    #     'one_to_one.tests.OneToOneTests.test_create_models_m2m',  # noqa
    #     # AssertionError: Sequences differ: <QuerySet []> != [<Waiter: Joe the waiter at Demon Dogs the restaurant>]
    #     'one_to_one.tests.OneToOneTests.test_foreign_key',  # noqa
    #     # one_to_one.models.Restaurant.DoesNotExist: Restaurant matching query does not exist.
    #     'one_to_one.tests.OneToOneTests.test_manager_get',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1444508500162408010}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_nullable_o2o_delete',  # noqa
    #     # KeyError: 'place'
    #     'one_to_one.tests.OneToOneTests.test_rel_pk_subquery',  # noqa
    #     # one_to_one.models.Director.DoesNotExist: Director matching query does not exist.
    #     'one_to_one.tests.OneToOneTests.test_related_object',  # noqa
    #     # one_to_one.models.Place.restaurant.RelatedObjectDoesNotExist: Place has no restaurant.
    #     'one_to_one.tests.OneToOneTests.test_related_object_cache',  # noqa
    #     # one_to_one.models.Place.DoesNotExist: Place matching query does not exist.
    #     'one_to_one.tests.OneToOneTests.test_related_object_cached_when_reverse_is_accessed',  # noqa
    #     # KeyError: 'place'
    #     'one_to_one.tests.OneToOneTests.test_reverse_object_cached_when_related_is_accessed',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:943045842421092922}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_reverse_object_cached_when_related_is_unset',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'one_to_one.tests.OneToOneTests.test_reverse_object_does_not_exist_cache',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:384310892827078104}) due to previously existing row
    #     'one_to_one.tests.OneToOneTests.test_reverse_relationship_cache_cascade',  # noqa
    #     # one_to_one.models.UndergroundBar.DoesNotExist: UndergroundBar matching query does not exist.
    #     'one_to_one.tests.OneToOneTests.test_save_nullable_o2o_after_parent',  # noqa
    #     # KeyError: 'place'
    #     'one_to_one.tests.OneToOneTests.test_setter',  # noqa
    #     # one_to_one.models.Waiter.DoesNotExist: Waiter matching query does not exist.
    #     'one_to_one.tests.OneToOneTests.test_update_one_to_one_pk',  # noqa
    #     # AssertionError: Lists differ: [] != ['Hello']
    #     'or_lookups.tests.OrLookupsTests.test_complex_filter',  # noqa
    #     # or_lookups.models.Article.DoesNotExist: Article matching query does not exist.
    #     'or_lookups.tests.OrLookupsTests.test_other_arg_queries',  # noqa
    #     # AssertionError: Lists differ: [] != ['Hello', 'Goodbye']
    #     'or_lookups.tests.OrLookupsTests.test_pk_q',  # noqa
    #     # AssertionError: Lists differ: ['Hello', 'Goodbye', 'Hello and goodbye'] != ['Hello', 'Hello and goodbye']
    #     'or_lookups.tests.OrLookupsTests.test_q_negated',  # noqa
    #     # System check identified no issues (0 silenced).
    #     'proxy_model_inheritance.tests.MultiTableInheritanceProxyTest.test_deletion_through_intermediate_proxy',  # noqa
    #     # proxy_models.models.MyPerson.DoesNotExist: MyPerson matching query does not exist.
    #     'proxy_models.tests.ProxyModelTests.test_basic_proxy',  # noqa
    #     # AssertionError: Lists differ: ['George', 'Bruce'] != ['Bruce', 'George']
    #     'proxy_models.tests.ProxyModelTests.test_proxy_delete',  # noqa
    #     # AssertionError: 0 != 1 : 0 queries executed, 1 expected
    #     'proxy_models.tests.ProxyModelTests.test_proxy_update',  # noqa
    #     # System check identified no issues (1 silenced).
    #     'raw_query.tests.RawQueryTests.test_missing_fields',  # noqa
    #     # select_related_regress.models.State.DoesNotExist: State matching query does not exist.
    #     'select_related_regress.tests.SelectRelatedRegressTests.test_regression_12851',  # noqa
    #     # KeyError: 'start'
    #     'select_related_regress.tests.SelectRelatedRegressTests.test_regression_7110',  # noqa
    #     # KeyError: 'status'
    #     'select_related_regress.tests.SelectRelatedRegressTests.test_regression_8036',  # noqa
    #     # google.api_core.exceptions.AlreadyExists: 409 Failed to insert row with primary key ({pk#id:1697029550452825661}) due to previously existing row
    #     'signals.tests.SignalTests.test_save_signals',  # noqa
    #     # System check identified no issues (0 silenced).
    #     'timezones.tests.NewDatabaseTests.test_update_with_timedelta',  # noqa
    #     "serializers.test_json.JsonSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_json.JsonSerializerTestCase.test_serialize_with_null_pk",
    #     "serializers.test_xml.XmlSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_xml.XmlSerializerTestCase.test_serialize_with_null_pk",
    #     "serializers.test_yaml.YamlSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_yaml.YamlSerializerTestCase.test_serialize_with_null_pk",
    #     # Tests that assume a serial pk.
    #     "servers.tests.LiveServerDatabase.test_fixtures_loaded",
    #     "sitemaps_tests.test_http.HTTPSitemapTests.test_alternate_language_for_item_i18n_sitemap",
    #     "sitemaps_tests.test_http.HTTPSitemapTests.test_language_for_item_i18n_sitemap",
    #     "syndication_tests.tests.SyndicationFeedTest.test_latest_post_date",
    #     "syndication_tests.tests.SyndicationFeedTest.test_rss091_feed",
    #     "syndication_tests.tests.SyndicationFeedTest.test_rss2_feed",
    #     "syndication_tests.tests.SyndicationFeedTest.test_template_feed",
    #     # Tests that expect it to be empty until saved in db.
    #     "test_utils.test_testcase.TestDataTests.test_class_attribute_identity",
    #     # Tests that require transactions.
    #     "test_utils.tests.CaptureOnCommitCallbacksTests.test_execute",
    #     "test_utils.tests.CaptureOnCommitCallbacksTests.test_no_arguments",
    #     "test_utils.tests.CaptureOnCommitCallbacksTests.test_pre_callback",
    #     "test_utils.tests.CaptureOnCommitCallbacksTests.test_using",
    #     "test_utils.tests.TestBadSetUpTestData.test_failure_in_setUpTestData_should_rollback_transaction",
    #     "timezones.tests.AdminTests.test_change_editable",
    #     "timezones.tests.AdminTests.test_change_editable_in_other_timezone",
    #     "timezones.tests.AdminTests.test_change_readonly",
    #     "timezones.tests.AdminTests.test_change_readonly_in_other_timezone",
    #     "timezones.tests.AdminTests.test_changelist",
    #     "timezones.tests.AdminTests.test_changelist_in_other_timezone",
    #     "timezones.tests.LegacyDatabaseTests.test_cursor_execute_accepts_naive_datetime",
    #     "timezones.tests.LegacyDatabaseTests.test_cursor_execute_returns_naive_datetime",
    #     # Spanner does not support iso_week_day but week_day is supported.
    #     "timezones.tests.LegacyDatabaseTests.test_query_datetime_lookups",
    #     "timezones.tests.NewDatabaseTests.test_aware_time_unsupported",
    #     "timezones.tests.NewDatabaseTests.test_cursor_execute_accepts_naive_datetime",
    #     "timezones.tests.NewDatabaseTests.test_cursor_execute_returns_naive_datetime",
    #     # datetimes retrieved from the database with the wrong hour when
    #     # USE_TZ = True: https://github.com/googleapis/python-spanner-django/issues/193
    #     "timezones.tests.NewDatabaseTests.test_query_convert_timezones",
    #     "timezones.tests.NewDatabaseTests.test_query_datetime_lookups",
    #     "timezones.tests.NewDatabaseTests.test_query_datetime_lookups_in_other_timezone",
    #     # extract() with timezone not working as expected:
    #     # https://github.com/googleapis/python-spanner-django/issues/191
    #     "timezones.tests.NewDatabaseTests.test_query_datetimes",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_discards_hooks_from_rolled_back_savepoint",
    #     # Tests that require transactions.
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_does_not_execute_if_transaction_rolled_back",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_hooks_cleared_after_rollback",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_hooks_cleared_on_reconnect",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_does_not_affect_outer",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_rolled_back_with_outer",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_no_hooks_run_from_failed_transaction",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_no_savepoints_atomic_merged_with_outer",
    #     "validation.test_custom_messages.CustomMessagesTests.test_custom_null_message",
    #     "validation.test_custom_messages.CustomMessagesTests.test_custom_simple_validator_message",
    #     "validation.test_unique.PerformUniqueChecksTest.test_primary_key_unique_check_not_performed_when_adding_and_pk_not_specified",  # noqa
    #     "validation.test_unique.PerformUniqueChecksTest.test_primary_key_unique_check_not_performed_when_not_adding",
    #     "validation.test_validators.TestModelsWithValidators.test_custom_validator_passes_for_correct_value",
    #     "validation.test_validators.TestModelsWithValidators.test_custom_validator_raises_error_for_incorrect_value",
    #     "validation.test_validators.TestModelsWithValidators.test_field_validators_can_be_any_iterable",
    #     "backends.tests.FkConstraintsTests.test_check_constraints",
    #     "fixtures_regress.tests.TestFixtures.test_loaddata_raises_error_when_fixture_has_invalid_foreign_key",
    #     "backends.tests.BackendTestCase.test_cursor_executemany_with_empty_params_list",
    #     "basic.tests.SelectOnSaveTests.test_select_on_save_lying_update",
    #     "basic.tests.ModelTest.test_hash",
    #     "custom_managers.tests.CustomManagerTests.test_slow_removal_through_specified_fk_related_manager",
    #     "custom_managers.tests.CustomManagerTests.test_slow_removal_through_default_fk_related_manager",
    #     "generic_relations.test_forms.GenericInlineFormsetTests.test_options",
    #     "generic_relations.tests.GenericRelationsTests.test_add_bulk_false",
    #     "generic_relations.tests.GenericRelationsTests.test_generic_update_or_create_when_updated",
    #     "generic_relations.tests.GenericRelationsTests.test_update_or_create_defaults",
    #     "m2m_through_regress.tests.ToFieldThroughTests.test_m2m_relations_unusable_on_null_pk_obj",
    #     "many_to_many.tests.ManyToManyTests.test_add",
    #     "many_to_one.tests.ManyToOneTests.test_fk_assignment_and_related_object_cache",
    #     "many_to_one.tests.ManyToOneTests.test_relation_unsaved",
    #     "model_fields.test_durationfield.TestSerialization.test_dumping",
    #     "model_fields.test_uuid.TestSerialization.test_dumping",
    #     "model_fields.test_booleanfield.ValidationTest.test_nullbooleanfield_blank",
    #     "model_inheritance.tests.ModelInheritanceTests.test_create_child_no_update",
    #     "model_regress.tests.ModelTests.test_get_next_prev_by_field_unsaved",
    #     "one_to_one.tests.OneToOneTests.test_get_reverse_on_unsaved_object",
    #     "one_to_one.tests.OneToOneTests.test_o2o_primary_key_delete",
    #     "one_to_one.tests.OneToOneTests.test_set_reverse_on_unsaved_object",
    #     "one_to_one.tests.OneToOneTests.test_unsaved_object",
    #     "queries.test_bulk_update.BulkUpdateNoteTests.test_unsaved_models",
    #     "expressions_case.tests.CaseExpressionTests.test_update_decimal",
    #     "serializers.test_json.JsonSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_json.JsonSerializerTestCase.test_serialize_with_null_pk",
    #     "serializers.test_xml.XmlSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_xml.XmlSerializerTestCase.test_serialize_with_null_pk",
    #     "serializers.test_yaml.YamlSerializerTestCase.test_pkless_serialized_strings",
    #     "serializers.test_yaml.YamlSerializerTestCase.test_serialize_with_null_pk",
    #     "serializers.test_data.SerializerDataTests.test_yaml_serializer",
    #     "serializers.test_data.SerializerDataTests.test_xml_serializer",
    #     "serializers.test_data.SerializerDataTests.test_python_serializer",
    #     "serializers.test_data.SerializerDataTests.test_json_serializer",
    #     "timezones.tests.LegacyDatabaseTests.test_cursor_execute_accepts_naive_datetime",
    #     "timezones.tests.NewDatabaseTests.test_cursor_execute_accepts_naive_datetime",
    #     "timezones.tests.AdminTests.test_change_editable",
    #     "timezones.tests.AdminTests.test_change_editable_in_other_timezone",
    #     "timezones.tests.AdminTests.test_change_readonly",
    #     "timezones.tests.AdminTests.test_change_readonly_in_other_timezone",
    #     "timezones.tests.AdminTests.test_changelist",
    #     "timezones.tests.AdminTests.test_changelist_in_other_timezone",
    #     "timezones.tests.LegacyDatabaseTests.test_cursor_execute_returns_naive_datetime",
    #     "timezones.tests.NewDatabaseTests.test_cursor_execute_returns_naive_datetime",
    #     "validation.test_custom_messages.CustomMessagesTests.test_custom_null_message",
    #     "validation.test_custom_messages.CustomMessagesTests.test_custom_simple_validator_message",
    #     "validation.test_unique.PerformUniqueChecksTest.test_primary_key_unique_check_not_performed_when_adding_and_pk_not_specified",
    #     "validation.test_unique.PerformUniqueChecksTest.test_primary_key_unique_check_not_performed_when_not_adding",
    #     "validation.test_validators.TestModelsWithValidators.test_custom_validator_passes_for_correct_value",
    #     "validation.test_validators.TestModelsWithValidators.test_custom_validator_raises_error_for_incorrect_value",
    #     "validation.test_validators.TestModelsWithValidators.test_field_validators_can_be_any_iterable",
    #     "servers.tests.LiveServerDatabase.test_fixtures_loaded",
    #     "admin_filters.tests.ListFiltersTests.test_booleanfieldlistfilter_nullbooleanfield",
    #     "admin_filters.tests.ListFiltersTests.test_booleanfieldlistfilter_tuple",
    #     "admin_filters.tests.ListFiltersTests.test_booleanfieldlistfilter",
    #     "admin_filters.tests.ListFiltersTests.test_datefieldlistfilter_with_time_zone_support",
    #     "admin_filters.tests.ListFiltersTests.test_datefieldlistfilter",
    #     "admin_filters.tests.ListFiltersTests.test_fieldlistfilter_underscorelookup_tuple",
    #     "admin_filters.tests.ListFiltersTests.test_fk_with_to_field",
    #     "admin_filters.tests.ListFiltersTests.test_listfilter_genericrelation",
    #     "admin_filters.tests.ListFiltersTests.test_lookup_with_non_string_value_underscored",
    #     "admin_filters.tests.ListFiltersTests.test_lookup_with_non_string_value",
    #     "admin_filters.tests.ListFiltersTests.test_relatedfieldlistfilter_manytomany",
    #     "admin_filters.tests.ListFiltersTests.test_simplelistfilter",
    #     "admin_inlines.tests.TestInline.test_inline_hidden_field_no_column",
    #     "proxy_models.tests.ProxyModelAdminTests.test_delete_str_in_model_admin",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_change_message",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_change_message_localized_datetime_input",
    #     "admin_utils.test_logentry.LogEntryTests.test_proxy_model_content_type_is_used_for_log_entries",
    #     "admin_utils.test_logentry.LogEntryTests.test_action_flag_choices",
    #     "admin_utils.test_logentry.LogEntryTests.test_log_action",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_change_message_formsets",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_change_message_not_json",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_get_admin_url",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_get_edited_object",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_repr",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_save",
    #     "admin_utils.test_logentry.LogEntryTests.test_logentry_unicode",
    #     "admin_utils.test_logentry.LogEntryTests.test_recentactions_without_content_type",
    #     "admin_views.tests.AdminViewPermissionsTest.test_history_view",
    #     "aggregation.test_filter_argument.FilteredAggregateTests.test_plain_annotate",
    #     "aggregation.tests.AggregateTestCase.test_annotate_basic",
    #     "aggregation.tests.AggregateTestCase.test_annotation",
    #     "aggregation.tests.AggregateTestCase.test_filtering",
    #     "aggregation_regress.tests.AggregationTests.test_more_more",
    #     "aggregation_regress.tests.AggregationTests.test_more_more_more",
    #     "defer_regress.tests.DeferRegressionTest.test_ticket_12163",
    #     "defer_regress.tests.DeferRegressionTest.test_ticket_23270",
    #     "distinct_on_fields.tests.DistinctOnTests.test_basic_distinct_on",
    #     "extra_regress.tests.ExtraRegressTests.test_regression_7314_7372",
    #     "generic_relations_regress.tests.GenericRelationTests.test_annotate",
    #     "get_earliest_or_latest.tests.TestFirstLast",
    #     "known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_multi_prefetch_related",
    #     "known_related_objects.tests.ExistingRelatedInstancesTests.test_reverse_one_to_one_multi_select_related",
    #     "lookup.tests.LookupTests.test_get_next_previous_by",
    #     "lookup.tests.LookupTests.test_values_list",
    #     "migrations.test_operations.OperationTests.test_alter_order_with_respect_to",
    #     "model_fields.tests.GetChoicesOrderingTests.test_get_choices_reverse_related_field",
    #     "model_formsets.tests.ModelFormsetTest.test_custom_pk",
    #     "model_formsets_regress.tests.FormfieldShouldDeleteFormTests.test_custom_delete",
    #     "multiple_database.tests.RouterTestCase.test_generic_key_cross_database_protection",
    #     "ordering.tests.OrderingTests.test_default_ordering_by_f_expression",
    #     "ordering.tests.OrderingTests.test_order_by_fk_attname",
    #     "ordering.tests.OrderingTests.test_order_by_override",
    #     "ordering.tests.OrderingTests.test_order_by_pk",
    #     "prefetch_related.test_prefetch_related_objects.PrefetchRelatedObjectsTests.test_m2m_then_m2m",
    #     "prefetch_related.tests.CustomPrefetchTests.test_custom_qs",
    #     "prefetch_related.tests.CustomPrefetchTests.test_nested_prefetch_related_are_not_overwritten",
    #     "prefetch_related.tests.ForeignKeyToFieldTest.test_m2m",
    #     "queries.test_bulk_update.BulkUpdateNoteTests.test_multiple_fields",
    #     "queries.test_bulk_update.BulkUpdateTests.test_inherited_fields",
    #     "queries.tests.Queries4Tests.test_ticket15316_exclude_true",
    #     "queries.tests.Queries5Tests.test_ticket7256",
    #     "queries.tests.SubqueryTests.test_related_sliced_subquery",
    #     "queries.tests.Ticket14056Tests.test_ticket_14056",
    #     "queries.tests.RelatedLookupTypeTests.test_values_queryset_lookup",
    #     "raw_query.tests.RawQueryTests.test_annotations",
    #     "raw_query.tests.RawQueryTests.test_get_item",
    #     "select_related.tests.SelectRelatedTests.test_field_traversal",
    #     "syndication_tests.tests.SyndicationFeedTest.test_rss2_feed",
    #     "syndication_tests.tests.SyndicationFeedTest.test_latest_post_date",
    #     "syndication_tests.tests.SyndicationFeedTest.test_rss091_feed",
    #     "syndication_tests.tests.SyndicationFeedTest.test_template_feed",
    #     "datetimes.tests.DateTimesTests.test_21432",
    #     "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_func_with_timezone",
    #     "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_timezone_applied_before_truncation",
    #     "timezones.tests.NewDatabaseTests.test_query_datetimes",
    #     "annotations.tests.NonAggregateAnnotationTestCase.test_combined_annotation_commutative",
    #     "db_functions.comparison.test_cast.CastTests.test_cast_to_decimal_field",
    #     "model_fields.test_decimalfield.DecimalFieldTests.test_fetch_from_db_without_float_rounding",
    #     "model_fields.test_decimalfield.DecimalFieldTests.test_roundtrip_with_trailing_zeros",
    #     # functions on full population.
    #     # SELECT list expression references <column> which is neither grouped
    #     # nor aggregated: https://github.com/googleapis/python-spanner-django/issues/245
    #     # ",
    #     # and DATE: https://github.com/googleapis/python-spanner-django/issues/255
    #     # duration arithmetic fails with dates: No matching signature for
    #     # function TIMESTAMP_ADD: https://github.com/googleapis/python-spanner-django/issues/253
    #     # This test doesn",
    #     # support select for update either (besides the ",
    #     # restriction).
    #     # integer division produces a float result, which can",
    #     "expressions.tests.ExpressionOperatorTests.test_lefthand_division",
    #     "expressions.tests.ExpressionOperatorTests.test_right_hand_division",
    #     # an integer column:
    #     # https://github.com/googleapis/python-spanner-django/issues/331
    #     # Cloud Spanner",
    #     # is unspecified unless these operators are used after ORDER BY.",
    #     "aggregation_regress.tests.AggregationTests.test_sliced_conditional_aggregate",
    #     "queries.tests.QuerySetBitwiseOperationTests.test_or_with_both_slice",
    #     "queries.tests.QuerySetBitwiseOperationTests.test_or_with_both_slice_and_ordering",
    #     "queries.tests.QuerySetBitwiseOperationTests.test_or_with_lhs_slice",
    #     "queries.tests.QuerySetBitwiseOperationTests.test_or_with_rhs_slice",
    #     "queries.tests.SubqueryTests.test_slice_subquery_and_query",
    #     # allowed limit of 1000.",
    #     "queries.test_bulk_update.BulkUpdateTests.test_large_batch",
    #     # casting DateField to DateTimeField adds an unexpected hour:
    #     # https://github.com/googleapis/python-spanner-django/issues/260
    #     # Tests that fail during tear down on databases that don",
    #     "contenttypes_tests.test_models.ContentTypesMultidbTests.test_multidb",
    #     "cache.tests.CreateCacheTableForDBCacheTests",
    #     "cache.tests.DBCacheTests",
    #     "cache.tests.DBCacheWithTimeZoneTests",
    #     "delete.tests.DeletionTests.test_queryset_delete_returns_num_rows",
    #     "delete.tests.DeletionTests.test_model_delete_returns_num_rows",
    #     "delete.tests.DeletionTests.test_deletion_order",
    #     "delete.tests.FastDeleteTests.test_fast_delete_empty_no_update_can_self_select",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_does_not_execute_if_transaction_rolled_back",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_hooks_cleared_after_rollback",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_hooks_cleared_on_reconnect",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_no_hooks_run_from_failed_transaction",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_no_savepoints_atomic_merged_with_outer",
    #     "get_or_create.tests.UpdateOrCreateTests.test_integrity",
    #     "get_or_create.tests.UpdateOrCreateTests.test_manual_primary_key_test",
    #     "get_or_create.tests.UpdateOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key",
    #     "test_utils.tests.TestBadSetUpTestData.test_failure_in_setUpTestData_should_rollback_transaction",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_discards_hooks_from_rolled_back_savepoint",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_rolled_back_with_outer",
    #     "transaction_hooks.tests.TestConnectionOnCommit.test_inner_savepoint_does_not_affect_outer",
    #     "introspection.tests.IntrospectionTests.test_sequence_list",
    #     "backends.tests.BackendTestCase.test_cursor_execute_with_pyformat",
    #     "backends.tests.BackendTestCase.test_cursor_executemany_with_pyformat",
    #     "backends.tests.BackendTestCase.test_cursor_executemany_with_pyformat_iterator",
    #     "migrations.test_commands.MigrateTests.test_migrate_fake_initial",
    #     "migrations.test_commands.MigrateTests.test_migrate_initial_false",
    #     "migrations.test_executor.ExecutorTests.test_soft_apply",
    #     "migrations.test_executor.ExecutorTests.test_alter_id_type_with_fk",
    #     "schema.tests.SchemaTests.test_alter_auto_field_to_char_field",
    #     "schema.tests.SchemaTests.test_alter_text_field_to_date_field",
    #     "schema.tests.SchemaTests.test_alter_text_field_to_datetime_field",
    #     "schema.tests.SchemaTests.test_alter_text_field_to_time_field",
    #     "contenttypes_tests.test_operations.ContentTypeOperationsTests",
    #     "migrations.test_operations.OperationTests.test_alter_fk_non_fk",
    #     "migrations.test_operations.OperationTests.test_alter_model_table",
    #     "migrations.test_operations.OperationTests.test_alter_model_table_m2m",
    #     "migrations.test_operations.OperationTests.test_rename_field",
    #     "migrations.test_operations.OperationTests.test_rename_field_reloads_state_on_fk_target_changes",
    #     "migrations.test_operations.OperationTests.test_rename_m2m_model_after_rename_field",
    #     "migrations.test_operations.OperationTests.test_rename_m2m_target_model",
    #     "migrations.test_operations.OperationTests.test_rename_m2m_through_model",
    #     "migrations.test_operations.OperationTests.test_rename_model",
    #     "migrations.test_operations.OperationTests.test_rename_model_with_m2m",
    #     "migrations.test_operations.OperationTests.test_rename_model_with_self_referential_fk",
    #     "migrations.test_operations.OperationTests.test_rename_model_with_self_referential_m2m",
    #     "migrations.test_operations.OperationTests.test_rename_model_with_superclass_fk",
    #     "migrations.test_operations.OperationTests.test_repoint_field_m2m",
    #     "schema.tests.SchemaTests.test_alter_db_table_case",
    #     "schema.tests.SchemaTests.test_alter_pk_with_self_referential_field",
    #     "schema.tests.SchemaTests.test_rename",
    #     "schema.tests.SchemaTests.test_db_table",
    #     "schema.tests.SchemaTests.test_m2m_rename_field_in_target_model",
    #     "schema.tests.SchemaTests.test_m2m_repoint",
    #     "schema.tests.SchemaTests.test_m2m_repoint_custom",
    #     "schema.tests.SchemaTests.test_m2m_repoint_inherited",
    #     "schema.tests.SchemaTests.test_rename_column_renames_deferred_sql_references",
    #     "schema.tests.SchemaTests.test_rename_keep_null_status",
    #     "schema.tests.SchemaTests.test_rename_referenced_field",
    #     "schema.tests.SchemaTests.test_rename_table_renames_deferred_sql_references",
    #     "schema.tests.SchemaTests.test_referenced_field_without_constraint_rename_inside_atomic_block",
    #     "schema.tests.SchemaTests.test_referenced_table_without_constraint_rename_inside_atomic_block",
    #     "schema.tests.SchemaTests.test_unique_name_quoting",
    #     "schema.tests.SchemaTests.test_alter_not_unique_field_to_primary_key",
    #     "schema.tests.SchemaTests.test_primary_key",
    #     "schema.tests.SchemaTests.test_alter_int_pk_to_int_unique",
    #     "migrations.test_executor.ExecutorTests.test_atomic_operation_in_non_atomic_migration",
    #     # https://github.com/googleapis/python-spanner-django/issues/378
    #     # parsing INSERT with one inlined value and one placeholder fails:
    #     # https://github.com/googleapis/python-spanner-django/issues/393
    #     # This test doesn",
    #     "multiple_database.tests.AuthTestCase",
    #     "migrations.test_loader.LoaderTests.test_loading_squashed",
    #     "model_inheritance_regress.tests.ModelInheritanceTest.test_issue_6755",
    #     "model_forms.tests.ModelFormBasicTests.test_runtime_choicefield_populated",
    #     "model_forms.tests.ModelFormBasicTests.test_multi_fields",
    #     "model_forms.tests.ModelFormBasicTests.test_m2m_initial_callable",
    #     "model_forms.tests.ModelFormBasicTests.test_initial_values",
    #     "model_forms.tests.OtherModelFormTests.test_prefetch_related_queryset",
    #     "model_formsets.tests.ModelFormsetTest.test_prevent_change_outer_model_and_create_invalid_data",
    #     "model_formsets_regress.tests.FormfieldShouldDeleteFormTests.test_no_delete",
    #     "model_formsets_regress.tests.FormsetTests.test_extraneous_query_is_not_run",
    #     "model_formsets.tests.ModelFormsetTest.test_inline_formsets_with_custom_pk",
    #     "model_forms.tests.ModelFormBaseTest.test_exclude_and_validation",
    #     "model_forms.tests.UniqueTest.test_unique_together",
    #     "model_forms.tests.UniqueTest.test_override_unique_together_message",
    #     # Failing on kokoro but passes locally. Issue: Multiple queries executed expected 1.
    #     # Spanner does not support UUID field natively
    #     # Spanner does not support very long FK name: 400 Foreign Key name not valid
    #     # Spanner does not support setting a default value on columns.
    #     # Direct SQL query test that do not follow spanner syntax.
    #     # Insert sql with param variables using %(name)s parameter style is failing
    #     # https://github.com/googleapis/python-spanner/issues/542
    #     # Spanner autofield is replaced with uuid4 so validation is disabled
    #     # Spanner does not support deferred unique constraints
    #     # Spanner does not support JSON object query on fields.
    #     # Spanner gived SHA encryption output in bytes, django expects it in hex string format.
    #     # Spanner does not support RANDOM number generation function
    #     # Spanner supports order by id, but it",
    #     "model_forms.test_modelchoicefield.ModelChoiceFieldTests.test_choice_iterator_passes_model_to_widget",
    #     "queries.test_qs_combinators.QuerySetSetOperationTests.test_union_with_values_list_and_order",
    #     "ordering.tests.OrderingTests.test_order_by_self_referential_fk",
    #     "fixtures.tests.ForwardReferenceTests.test_forward_reference_m2m_natural_key",
    #     "fixtures.tests.ForwardReferenceTests.test_forward_reference_fk_natural_key",
    #     "backends.tests.BackendTestCase.test_cursor_executemany_with_empty_params_list",
    #     "annotations.tests.NonAggregateAnnotationTestCase.test_grouping_by_q_expression_annotation",
    #     "test_utils.test_testcase.TestDataTests.test_class_attribute_identity",
    #     "model_fields.test_jsonfield.TestSerialization.test_dumping",
    #     "model_fields.test_jsonfield.TestSerialization.test_dumping",
    #     "model_fields.test_jsonfield.TestSerialization.test_dumping",
    #     "model_fields.test_jsonfield.TestSerialization.test_xml_serialization",
    #     "model_fields.test_jsonfield.TestSerialization.test_xml_serialization",
    #     "model_fields.test_jsonfield.TestSerialization.test_xml_serialization",
    #     "bulk_create.tests.BulkCreateTests.test_unsaved_parent",
    #     "lookup.tests.LookupTests.test_exact_query_rhs_with_selected_columns",
    #     "prefetch_related.tests.DirectPrefetchedObjectCacheReuseTests.test_detect_is_fetched",
    #     "prefetch_related.tests.DirectPrefetchedObjectCacheReuseTests.test_detect_is_fetched_with_to_attr",
    #     "timezones.tests.NewDatabaseTests.test_query_convert_timezones",
    #     # Field: GenericIPAddressField is mapped to String in Spanner
    #     # BigIntegerField is mapped to IntegerField in Spanner
    #     # Spanner limitation: Cannot change type of column.
    #     # Spanner limitation: Cannot rename tables and columns.
    #     # Django 4 and 3 skips migrated:
    #     # Spanner does not support automatic coercion from float64 to int64
    # )

    if os.environ.get("SPANNER_EMULATOR_HOST", None):
        # Some code isn't yet supported by the Spanner emulator.
        skip_tests += (
            "admin_changelist.test_date_hierarchy.DateHierarchyTests.test_bounded_params",  # noqa
            # Untyped parameters are not supported:
            # https://github.com/GoogleCloudPlatform/cloud-spanner-emulator#features-and-limitations
            "admin_changelist.test_date_hierarchy.DateHierarchyTests.test_bounded_params_with_dst_time_zone",  # noqa
            "admin_changelist.test_date_hierarchy.DateHierarchyTests.test_bounded_params_with_time_zone",  # noqa
            "admin_changelist.test_date_hierarchy.DateHierarchyTests.test_invalid_params",  # noqa
            "admin_changelist.tests.ChangeListTests.test_builtin_lookup_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_changelist_search_form_validation",  # noqa
            "admin_changelist.tests.ChangeListTests.test_changelist_view_list_editable_changed_objects_uses_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_clear_all_filters_link",  # noqa
            "admin_changelist.tests.ChangeListTests.test_clear_all_filters_link_callable_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_computed_list_display_localization",  # noqa
            "admin_changelist.tests.ChangeListTests.test_custom_lookup_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_custom_lookup_with_pk_shortcut",  # noqa
            "admin_changelist.tests.ChangeListTests.test_custom_paginator",  # noqa
            "admin_changelist.tests.ChangeListTests.test_deterministic_order_for_model_ordered_by_its_manager",  # noqa
            "admin_changelist.tests.ChangeListTests.test_deterministic_order_for_unordered_model",  # noqa
            "admin_changelist.tests.ChangeListTests.test_dynamic_list_display",  # noqa
            "admin_changelist.tests.ChangeListTests.test_dynamic_list_display_links",  # noqa
            "admin_changelist.tests.ChangeListTests.test_dynamic_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_dynamic_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_get_edited_object_ids",  # noqa
            "admin_changelist.tests.ChangeListTests.test_get_list_editable_queryset",  # noqa
            "admin_changelist.tests.ChangeListTests.test_get_list_editable_queryset_with_regex_chars_in_prefix",  # noqa
            "admin_changelist.tests.ChangeListTests.test_get_select_related_custom_method",  # noqa
            "admin_changelist.tests.ChangeListTests.test_multiuser_edit",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_clear_all_filters_link",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_inherited_m2m_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_m2m_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_m2m_to_inherited_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_many_to_many_at_second_level_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_non_unique_related_object_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_non_unique_related_object_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_through_m2m_at_second_level_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_duplicates_for_through_m2m_in_list_filter",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_exists_for_m2m_in_list_filter_without_params",  # noqa
            "admin_changelist.tests.ChangeListTests.test_no_list_display_links",  # noqa
            "admin_changelist.tests.ChangeListTests.test_object_tools_displayed_no_add_permission",  # noqa
            "admin_changelist.tests.ChangeListTests.test_pagination",  # noqa
            "admin_changelist.tests.ChangeListTests.test_pagination_page_range",  # noqa
            "admin_changelist.tests.ChangeListTests.test_pk_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_editable",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_editable_html",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_empty_changelist_value",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_html",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_set_empty_value_display_in_model_admin",  # noqa
            "admin_changelist.tests.ChangeListTests.test_result_list_set_empty_value_display_on_admin_site",  # noqa
            "admin_changelist.tests.ChangeListTests.test_select_related_as_empty_tuple",  # noqa
            "admin_changelist.tests.ChangeListTests.test_select_related_as_tuple",  # noqa
            "admin_changelist.tests.ChangeListTests.test_select_related_preserved",  # noqa
            "admin_changelist.tests.ChangeListTests.test_show_all",  # noqa
            "admin_changelist.tests.ChangeListTests.test_spanning_relations_with_custom_lookup_in_search_fields",  # noqa
            "admin_changelist.tests.ChangeListTests.test_specified_ordering_by_f_expression",  # noqa
            "admin_changelist.tests.ChangeListTests.test_specified_ordering_by_f_expression_without_asc_desc",  # noqa
            "admin_changelist.tests.ChangeListTests.test_total_ordering_optimization",  # noqa
            "admin_changelist.tests.ChangeListTests.test_total_ordering_optimization_meta_constraints",  # noqa
            "admin_changelist.tests.ChangeListTests.test_tuple_list_display",  # noqa
            "admin_changelist.tests.GetAdminLogTests.test_no_user",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_add_with_GET_args",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_admin_URLs_no_clash",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_basic_add_GET",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_basic_add_POST",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_post_save_add_redirect",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_post_save_change_redirect",  # noqa
            "admin_custom_urls.tests.AdminCustomUrlsTest.test_post_url_continue",  # noqa
            "admin_docs.test_middleware.XViewMiddlewareTest.test_callable_object_view",  # noqa
            "admin_docs.test_middleware.XViewMiddlewareTest.test_no_auth_middleware",  # noqa
            "admin_docs.test_middleware.XViewMiddlewareTest.test_xview_class",  # noqa
            "admin_docs.test_middleware.XViewMiddlewareTest.test_xview_func",  # noqa
            "admin_docs.test_views.AdminDocViewDefaultEngineOnly.test_template_detail_path_traversal",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_bookmarklets",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_index",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_missing_docutils",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_model_index",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_namespaced_view_detail",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_no_sites_framework",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_template_detail",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_templatefilter_index",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_templatetag_index",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_view_detail",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_view_detail_as_method",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_view_detail_illegal_import",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_view_index",  # noqa
            "admin_docs.test_views.AdminDocViewTests.test_view_index_with_method",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_bookmarklets",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_index",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_missing_docutils",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_model_index",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_namespaced_view_detail",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_no_sites_framework",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_template_detail",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_templatefilter_index",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_templatetag_index",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_view_detail",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_view_detail_as_method",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_view_detail_illegal_import",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_view_index",  # noqa
            "admin_docs.test_views.AdminDocViewWithMultipleEngines.test_view_index_with_method",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_app_not_found",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_descriptions_render_correctly",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_instance_of_property_methods_are_displayed",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_method_data_types",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_method_excludes",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_methods_with_arguments",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_methods_with_arguments_display_arguments",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_methods_with_arguments_display_arguments_default_value",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_methods_with_multiple_arguments_display_arguments",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_model_detail_title",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_model_docstring_renders_correctly",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_model_not_found",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_model_with_many_to_one",  # noqa
            "admin_docs.test_views.TestModelDetailView.test_model_with_no_backward_relations_render_only_relevant_fields",  # noqa
            "admin_filters.tests.ListFiltersTests.test_relatedonlyfieldlistfilter_manytomany",  # noqa
            "admin_filters.tests.ListFiltersTests.test_relatedonlyfieldlistfilter_underscorelookup_foreignkey",  # noqa
            "admin_filters.tests.ListFiltersTests.test_simplelistfilter_with_none_returning_lookups",  # noqa
            "admin_filters.tests.ListFiltersTests.test_simplelistfilter_with_queryset_based_lookups",  # noqa
            "admin_filters.tests.ListFiltersTests.test_simplelistfilter_without_parameter",  # noqa
            "admin_filters.tests.ListFiltersTests.test_two_characters_long_field",  # noqa
            "admin_inlines.tests.TestInline.test_callable_lookup",  # noqa
            "admin_inlines.tests.TestInline.test_can_delete",  # noqa
            "admin_inlines.tests.TestInline.test_create_inlines_on_inherited_model",  # noqa
            "admin_inlines.tests.TestInline.test_custom_form_tabular_inline_extra_field_label",  # noqa
            "admin_inlines.tests.TestInline.test_custom_form_tabular_inline_label",  # noqa
            "admin_inlines.tests.TestInline.test_custom_form_tabular_inline_overridden_label",  # noqa
            "admin_inlines.tests.TestInline.test_custom_get_extra_form",  # noqa
            "admin_inlines.tests.TestInline.test_custom_min_num",  # noqa
            "admin_inlines.tests.TestInline.test_custom_pk_shortcut",  # noqa
            "admin_inlines.tests.TestInline.test_help_text",  # noqa
            "admin_inlines.tests.TestInline.test_inline_editable_pk",  # noqa
            "admin_inlines.tests.TestInline.test_inline_nonauto_noneditable_inherited_pk",  # noqa
            "admin_inlines.tests.TestInline.test_inline_nonauto_noneditable_pk",  # noqa
            "admin_inlines.tests.TestInline.test_inline_primary",  # noqa
            "admin_inlines.tests.TestInline.test_inlines_show_change_link_registered",  # noqa
            "admin_inlines.tests.TestInline.test_inlines_show_change_link_unregistered",  # noqa
            "admin_inlines.tests.TestInline.test_inlines_singular_heading_one_to_one",  # noqa
            "admin_inlines.tests.TestInline.test_localize_pk_shortcut",  # noqa
            "admin_inlines.tests.TestInline.test_many_to_many_inlines",  # noqa
            "admin_inlines.tests.TestInline.test_min_num",  # noqa
            "admin_inlines.tests.TestInline.test_no_parent_callable_lookup",  # noqa
            "admin_inlines.tests.TestInline.test_non_editable_custom_form_tabular_inline_extra_field_label",  # noqa
            "admin_inlines.tests.TestInline.test_non_related_name_inline",  # noqa
            "admin_inlines.tests.TestInline.test_noneditable_inline_has_field_inputs",  # noqa
            "admin_inlines.tests.TestInline.test_readonly_stacked_inline_label",  # noqa
            "admin_inlines.tests.TestInline.test_stacked_inline_edit_form_contains_has_original_class",  # noqa
            "admin_inlines.tests.TestInline.test_tabular_inline_column_css_class",  # noqa
            "admin_inlines.tests.TestInline.test_tabular_inline_show_change_link_false_registered",  # noqa
            "admin_inlines.tests.TestInline.test_tabular_model_form_meta_readonly_field",  # noqa
            "admin_inlines.tests.TestInline.test_tabular_non_field_errors",  # noqa
            "admin_inlines.tests.TestInlineMedia.test_all_inline_media",  # noqa
            "admin_inlines.tests.TestInlineMedia.test_inline_media_only_base",  # noqa
            "admin_inlines.tests.TestInlineMedia.test_inline_media_only_inline",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_add_fk_add_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_add_fk_noperm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_add_m2m_add_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_add_m2m_noperm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_add_m2m_view_only_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_add_change_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_add_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_all_perms",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_change_del_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_change_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_fk_noperm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_m2m_add_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_m2m_change_perm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_m2m_noperm",  # noqa
            "admin_inlines.tests.TestInlinePermissions.test_inline_change_m2m_view_only_perm",  # noqa
            "admin_inlines.tests.TestInlineProtectedOnDelete.test_deleting_inline_with_protected_delete_does_not_validate",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_add_url_not_allowed",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_extra_inlines_are_not_shown",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_get_to_change_url_is_allowed",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_inline_delete_buttons_are_not_shown",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_inlines_are_rendered_as_read_only",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_main_model_is_rendered_as_read_only",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_post_to_change_url_not_allowed",  # noqa
            "admin_inlines.tests.TestReadOnlyChangeViewInlinePermissions.test_submit_line_shows_only_close_button",  # noqa
            "admin_ordering.tests.TestAdminOrdering.test_dynamic_ordering",  # noqa
            "admin_views.test_multidb.MultiDatabaseTests.test_delete_view",  # noqa
            "aggregation.tests.AggregateTestCase.test_add_implementation",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregate_alias",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregate_annotation",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregate_in_order_by",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregate_multi_join",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregate_over_complex_annotation",  # noqa
            "aggregation.tests.AggregateTestCase.test_aggregation_expressions",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_defer",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_defer_select_related",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_m2m",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_ordering",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_over_annotate",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_values",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_values_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotate_values_list",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotated_aggregate_over_annotated_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_annotation_expressions",  # noqa
            "aggregation.tests.AggregateTestCase.test_arguments_must_be_expressions",  # noqa
            "aggregation.tests.AggregateTestCase.test_avg_decimal_field",  # noqa
            "aggregation.tests.AggregateTestCase.test_avg_duration_field",  # noqa
            "aggregation.tests.AggregateTestCase.test_backwards_m2m_annotate",  # noqa
            "aggregation.tests.AggregateTestCase.test_combine_different_types",  # noqa
            "aggregation.tests.AggregateTestCase.test_complex_aggregations_require_kwarg",  # noqa
            "aggregation.tests.AggregateTestCase.test_complex_values_aggregation",  # noqa
            "aggregation.tests.AggregateTestCase.test_count",  # noqa
            "aggregation.tests.AggregateTestCase.test_count_distinct_expression",  # noqa
            "aggregation.tests.AggregateTestCase.test_count_star",  # noqa
            "aggregation.tests.AggregateTestCase.test_dates_with_aggregation",  # noqa
            "aggregation.tests.AggregateTestCase.test_empty_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_even_more_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_expression_on_aggregation",  # noqa
            "aggregation.tests.AggregateTestCase.test_filter_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_fkey_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_grouped_annotation_in_group_by",  # noqa
            "aggregation.tests.AggregateTestCase.test_more_aggregation",  # noqa
            "aggregation.tests.AggregateTestCase.test_multi_arg_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_multiple_aggregates",  # noqa
            "aggregation.tests.AggregateTestCase.test_non_grouped_annotation_not_in_group_by",  # noqa
            "aggregation.tests.AggregateTestCase.test_nonaggregate_aggregation_throws",  # noqa
            "aggregation.tests.AggregateTestCase.test_nonfield_annotation",  # noqa
            "aggregation.tests.AggregateTestCase.test_order_of_precedence",  # noqa
            "aggregation.tests.AggregateTestCase.test_reverse_fkey_annotate",  # noqa
            "aggregation.tests.AggregateTestCase.test_single_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_sum_distinct_aggregate",  # noqa
            "aggregation.tests.AggregateTestCase.test_sum_duration_field",  # noqa
            "aggregation.tests.AggregateTestCase.test_ticket11881",  # noqa
            "aggregation.tests.AggregateTestCase.test_ticket12886",  # noqa
            "aggregation.tests.AggregateTestCase.test_ticket17424",  # noqa
            "aggregation.tests.AggregateTestCase.test_values_aggregation",  # noqa
            "aggregation.tests.AggregateTestCase.test_values_annotation_with_expression",  # noqa
            "aggregation_regress.tests.JoinPromotionTests.test_ticket_21150",  # noqa
            "aggregation_regress.tests.SelfReferentialFKTests.test_ticket_24748",  # noqa
            "annotations.tests.NonAggregateAnnotationTestCase.test_custom_functions",  # noqa
            "annotations.tests.NonAggregateAnnotationTestCase.test_custom_functions_can_ref_other_functions",  # noqa
            "annotations.tests.NonAggregateAnnotationTestCase.test_filter_decimal_annotation",  # noqa
            # Untyped parameters are not supported:
            # https://github.com/GoogleCloudPlatform/cloud-spanner-emulator#features-and-limitations
            "auth_tests.test_admin_multidb.MultiDatabaseTests.test_add_view",  # noqa
            "auth_tests.test_auth_backends.AllowAllUsersModelBackendTest.test_authenticate",  # noqa
            "auth_tests.test_auth_backends.AllowAllUsersModelBackendTest.test_get_user",  # noqa
            "auth_tests.test_auth_backends.AuthenticateTests.test_authenticate_sensitive_variables",  # noqa
            "auth_tests.test_auth_backends.AuthenticateTests.test_clean_credentials_sensitive_variables",  # noqa
            "auth_tests.test_auth_backends.AuthenticateTests.test_skips_backends_with_decorated_method",  # noqa
            "auth_tests.test_auth_backends.AuthenticateTests.test_skips_backends_without_arguments",  # noqa
            "auth_tests.test_auth_backends.AuthenticateTests.test_type_error_raised",  # noqa
            "auth_tests.test_auth_backends.BaseBackendTest.test_get_all_permissions",  # noqa
            "auth_tests.test_auth_backends.BaseBackendTest.test_get_group_permissions",  # noqa
            "auth_tests.test_auth_backends.BaseBackendTest.test_get_user_permissions",  # noqa
            "auth_tests.test_auth_backends.BaseBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.ChangedBackendSettingsTest.test_changed_backend_settings",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_anonymous_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_authentication_timing",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_authentication_without_credentials",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_custom_perms",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_get_all_superuser_permissions",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_has_no_object_perm",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.CustomPermissionsUserModelBackendTest.test_inactive_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.CustomUserModelBackendAuthenticateTest.test_authenticate",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_anonymous_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_authentication_timing",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_authentication_without_credentials",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_custom_perms",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_get_all_superuser_permissions",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_has_no_object_perm",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.ExtensionUserModelBackendTest.test_inactive_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.ImportedBackendTests.test_backend_path",  # noqa
            "auth_tests.test_auth_backends.ImproperlyConfiguredUserModelTest.test_does_not_shadow_exception",  # noqa
            "auth_tests.test_auth_backends.InActiveUserBackendTest.test_has_module_perms",  # noqa
            "auth_tests.test_auth_backends.InActiveUserBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_anonymous_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_authenticate_inactive",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_authenticate_user_without_is_active_field",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_authentication_timing",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_authentication_without_credentials",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_custom_perms",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_get_all_superuser_permissions",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_has_no_object_perm",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.ModelBackendTest.test_inactive_has_no_permissions",  # noqa
            "auth_tests.test_auth_backends.NoBackendsTest.test_raises_exception",  # noqa
            "auth_tests.test_auth_backends.PermissionDeniedBackendTest.test_authenticates",  # noqa
            "auth_tests.test_auth_backends.PermissionDeniedBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.PermissionDeniedBackendTest.test_has_perm_denied",  # noqa
            "auth_tests.test_auth_backends.PermissionDeniedBackendTest.test_permission_denied",  # noqa
            "auth_tests.test_auth_backends.RowlevelBackendTest.test_get_all_permissions",  # noqa
            "auth_tests.test_auth_backends.RowlevelBackendTest.test_get_group_permissions",  # noqa
            "auth_tests.test_auth_backends.RowlevelBackendTest.test_has_perm",  # noqa
            "auth_tests.test_auth_backends.SelectingBackendTests.test_backend_path_login_with_explicit_backends",  # noqa
            "auth_tests.test_auth_backends.SelectingBackendTests.test_backend_path_login_without_authenticate_multiple_backends",  # noqa
            "auth_tests.test_auth_backends.SelectingBackendTests.test_backend_path_login_without_authenticate_single_backend",  # noqa
            "auth_tests.test_auth_backends.SelectingBackendTests.test_non_string_backend",  # noqa
            "auth_tests.test_auth_backends.UUIDUserTests.test_login",  # noqa
            "auth_tests.test_basic.BasicTestCase.test_superuser",  # noqa
            "auth_tests.test_basic.BasicTestCase.test_superuser_no_email_or_password",  # noqa
            "auth_tests.test_basic.BasicTestCase.test_unicode_username",  # noqa
            "auth_tests.test_basic.BasicTestCase.test_user",  # noqa
            "auth_tests.test_basic.BasicTestCase.test_user_no_email",  # noqa
            "auth_tests.test_basic.TestGetUser.test_get_user",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_message_attrs",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_perm_in_perms_attrs",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_perms_attrs",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_session_is_accessed",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_session_not_accessed",  # noqa
            "auth_tests.test_context_processors.AuthContextProcessorTests.test_user_attrs",  # noqa
            "auth_tests.test_decorators.LoginRequiredTestCase.test_callable",  # noqa
            "auth_tests.test_decorators.LoginRequiredTestCase.test_login_required",  # noqa
            "auth_tests.test_decorators.LoginRequiredTestCase.test_login_required_next_url",  # noqa
            "auth_tests.test_decorators.LoginRequiredTestCase.test_view",  # noqa
            "auth_tests.test_decorators.PermissionsRequiredDecoratorTest.test_many_permissions_in_set_pass",  # noqa
            "auth_tests.test_decorators.PermissionsRequiredDecoratorTest.test_many_permissions_pass",  # noqa
            "auth_tests.test_decorators.PermissionsRequiredDecoratorTest.test_permissioned_denied_exception_raised",  # noqa
            "auth_tests.test_decorators.PermissionsRequiredDecoratorTest.test_permissioned_denied_redirect",  # noqa
            "auth_tests.test_decorators.PermissionsRequiredDecoratorTest.test_single_permission_pass",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_missing_passwords",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_non_matching_passwords",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_one_password",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_password_whitespace_not_stripped",  # noqa
            "auth_tests.test_forms.AdminPasswordChangeFormTest.test_success",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_custom_login_allowed_policy",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_get_invalid_login_error",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_inactive_user",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_inactive_user_i18n",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_inactive_user_incorrect_password",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_integer_username",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_invalid_username",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_login_failed",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_password_whitespace_not_stripped",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_success",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_unicode_username",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_autocapitalize_none",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_label",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_label_empty_string",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_label_not_set",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_max_length_defaults_to_254",  # noqa
            "auth_tests.test_forms.AuthenticationFormTest.test_username_field_max_length_matches_user_model",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_both_passwords",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_custom_form",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_custom_form_hidden_username_field",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_custom_form_with_different_username_field",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_duplicate_normalized_unicode",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_invalid_data",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_normalize_username",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_password_help_text",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_password_verification",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_password_whitespace_not_stripped",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_success",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_unicode_username",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_user_already_exists",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_user_create_form_validates_password_with_all_data",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_username_field_autocapitalize_none",  # noqa
            "auth_tests.test_forms.BaseUserCreationFormTest.test_validates_password",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_field_order",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_incorrect_password",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_password_verification",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_password_whitespace_not_stripped",  # noqa
            "auth_tests.test_forms.PasswordChangeFormTest.test_success",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_cleaned_data",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_custom_email_constructor",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_custom_email_field",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_custom_email_subject",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_inactive_user",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_invalid_email",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_nonexistent_email",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_preserve_username_case",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_save_html_email_template_name",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_save_plaintext_email",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_unusable_password",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_user_email_domain_unicode_collision",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_user_email_domain_unicode_collision_nonexistent",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_user_email_unicode_collision",  # noqa
            "auth_tests.test_forms.PasswordResetFormTest.test_user_email_unicode_collision_nonexistent",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_help_text_translation",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_html_autocomplete_attributes",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_password_verification",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_password_whitespace_not_stripped",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_success",  # noqa
            "auth_tests.test_forms.SetPasswordFormTest.test_validates_password",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_14242",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_17944_empty_password",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_17944_unknown_password_algorithm",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_17944_unmanageable_password",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_19133",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_bug_19349_bound_password_field",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_custom_form",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_password_excluded",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_unusable_password",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_username_field_autocapitalize_none",  # noqa
            "auth_tests.test_forms.UserChangeFormTest.test_username_validity",  # noqa
            "auth_tests.test_handlers.ModWsgiHandlerTestCase.test_check_password",  # noqa
            "auth_tests.test_handlers.ModWsgiHandlerTestCase.test_check_password_custom_user",  # noqa
            "auth_tests.test_handlers.ModWsgiHandlerTestCase.test_groups_for_user",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_get_pass",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_get_pass_no_input",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_nonexistent_username",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_password_validation",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_system_username",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_that_changepassword_command_changes_joes_password",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_that_changepassword_command_works_with_nonascii_output",  # noqa
            "auth_tests.test_management.ChangepasswordManagementCommandTestCase.test_that_max_tries_exits_1",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_basic_usage",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_default_username",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_email_in_username",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_environment_variable_non_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_existing_username",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_existing_username_non_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_existing_username_provided_via_option_and_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_fields_with_fk",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_fields_with_fk_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_fields_with_m2m",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_fields_with_m2m_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_fields_with_m2m_interactive_blank",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_ignore_environment_variable_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_ignore_environment_variable_non_interactive",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_invalid_username",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_non_ascii_verbose_name",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_passing_stdin",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_password_validation",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_password_validation_bypass",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_swappable_user",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_swappable_user_username_non_unique",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_validate_password_against_required_fields",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_validate_password_against_username",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_validation_blank_password_entered",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_validation_mismatched_passwords",  # noqa
            "auth_tests.test_management.CreatesuperuserManagementCommandTestCase.test_verbosity_zero",  # noqa
            "auth_tests.test_management.GetDefaultUsernameTestCase.test_existing",  # noqa
            "auth_tests.test_management.GetDefaultUsernameTestCase.test_with_database",  # noqa
            "auth_tests.test_management.MultiDBChangepasswordManagementCommandTestCase.test_that_changepassword_command_with_database_option_uses_given_db",  # noqa
            "auth_tests.test_management.MultiDBCreatesuperuserTestCase.test_createsuperuser_command_suggested_username_with_database_option",  # noqa
            "auth_tests.test_management.MultiDBCreatesuperuserTestCase.test_createsuperuser_command_with_database_option",  # noqa
            "auth_tests.test_middleware.TestAuthenticationMiddleware.test_changed_password_invalidates_session",  # noqa
            "auth_tests.test_middleware.TestAuthenticationMiddleware.test_no_password_change_doesnt_invalidate_session",  # noqa
            "auth_tests.test_middleware.TestAuthenticationMiddleware.test_no_session",  # noqa
            "auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests.test_user_has_now_proxy_model_permissions",  # noqa
            "auth_tests.test_migrations.ProxyModelWithDifferentAppLabelTests.test_user_keeps_same_permissions_after_migrating_backward",  # noqa
            "auth_tests.test_migrations.ProxyModelWithSameAppLabelTests.test_user_keeps_same_permissions_after_migrating_backward",  # noqa
            "auth_tests.test_migrations.ProxyModelWithSameAppLabelTests.test_user_still_has_proxy_model_permissions",  # noqa
            "auth_tests.test_mixins.AccessMixinTests.test_access_mixin_permission_denied_response",  # noqa
            "auth_tests.test_mixins.AccessMixinTests.test_stacked_mixins_missing_permission",  # noqa
            "auth_tests.test_mixins.AccessMixinTests.test_stacked_mixins_not_logged_in",  # noqa
            "auth_tests.test_mixins.AccessMixinTests.test_stacked_mixins_success",  # noqa
            "auth_tests.test_mixins.LoginRequiredMixinTests.test_login_required",  # noqa
            "auth_tests.test_mixins.PermissionsRequiredMixinTests.test_many_permissions_pass",  # noqa
            "auth_tests.test_mixins.PermissionsRequiredMixinTests.test_permissioned_denied_exception_raised",  # noqa
            "auth_tests.test_mixins.PermissionsRequiredMixinTests.test_permissioned_denied_redirect",  # noqa
            "auth_tests.test_mixins.PermissionsRequiredMixinTests.test_single_permission_pass",  # noqa
            "auth_tests.test_models.AbstractUserTestCase.test_check_password_upgrade",  # noqa
            "auth_tests.test_models.AbstractUserTestCase.test_last_login_default",  # noqa
            "auth_tests.test_models.AbstractUserTestCase.test_user_double_save",  # noqa
            "auth_tests.test_models.IsActiveTestCase.test_builtin_user_isactive",  # noqa
            "auth_tests.test_models.IsActiveTestCase.test_is_active_field_default",  # noqa
            "auth_tests.test_models.NaturalKeysTestCase.test_user_natural_key",  # noqa
            "auth_tests.test_models.TestCreateSuperUserSignals.test_create_superuser",  # noqa
            "auth_tests.test_models.TestCreateSuperUserSignals.test_create_user",  # noqa
            "auth_tests.test_models.UserManagerTestCase.test_create_user",  # noqa
            "auth_tests.test_models.UserManagerTestCase.test_create_user_is_staff",  # noqa
            "auth_tests.test_models.UserManagerTestCase.test_runpython_manager_methods",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_backend_without_with_perm",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_basic",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_custom_backend",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_custom_backend_pass_obj",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_invalid_backend_type",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_invalid_permission_name",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_invalid_permission_type",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_multiple_backends",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_nonexistent_backend",  # noqa
            "auth_tests.test_models.UserWithPermTestCase.test_nonexistent_permission",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_csrf_validation_passes_after_process_request_login",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_unknown_user",  # noqa
            "auth_tests.test_remote_user.AllowAllUsersRemoteUserBackendTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_csrf_validation_passes_after_process_request_login",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_unknown_user",  # noqa
            "auth_tests.test_remote_user.CustomHeaderRemoteUserTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_csrf_validation_passes_after_process_request_login",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_unknown_user",  # noqa
            "auth_tests.test_remote_user.PersistentRemoteUserTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_csrf_validation_passes_after_process_request_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_unknown_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserCustomTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserNoCreateTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.RemoteUserNoCreateTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserNoCreateTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserNoCreateTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserNoCreateTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_csrf_validation_passes_after_process_request_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_header_disappears",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_inactive_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_known_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_last_login",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_unknown_user",  # noqa
            "auth_tests.test_remote_user.RemoteUserTest.test_user_switch_forces_new_login",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_failed_login_without_request",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_login",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_login_with_custom_user_without_last_login_field",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_logout",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_logout_anonymous",  # noqa
            "auth_tests.test_signals.SignalTestCase.test_update_last_login",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_change_done_view",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_change_view",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_complete_view",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_confirm_view_custom_username_hint",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_confirm_view_invalid_token",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_confirm_view_valid_token",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_done_view",  # noqa
            "auth_tests.test_templates.AuthTemplateTests.test_password_reset_view",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_10265",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_check_token_with_nonexistent_token_and_user",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_make_token",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_timeout",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_token_with_different_email",  # noqa
            "auth_tests.test_tokens.TokenGeneratorTest.test_token_with_different_secret",  # noqa
            "auth_tests.test_validators.UserAttributeSimilarityValidatorTest.test_validate",  # noqa
            "auth_tests.test_views.AuthViewNamedURLTests.test_named_urls",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_done_fails",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_done_succeeds",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_fails_with_invalid_old_password",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_fails_with_mismatched_passwords",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_redirect_custom",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_redirect_custom_named",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_redirect_default",  # noqa
            "auth_tests.test_views.ChangePasswordTest.test_password_change_succeeds",  # noqa
            "auth_tests.test_views.ChangelistTests.test_changelist_disallows_password_lookups",  # noqa
            "auth_tests.test_views.ChangelistTests.test_password_change_bad_url",  # noqa
            "auth_tests.test_views.ChangelistTests.test_user_change_different_user_password",  # noqa
            "auth_tests.test_views.ChangelistTests.test_user_change_email",  # noqa
            "auth_tests.test_views.ChangelistTests.test_user_change_password",  # noqa
            "auth_tests.test_views.ChangelistTests.test_user_change_password_passes_user_to_has_change_permission",  # noqa
            "auth_tests.test_views.ChangelistTests.test_user_not_change",  # noqa
            "auth_tests.test_views.ChangelistTests.test_view_user_password_is_readonly",  # noqa
            "auth_tests.test_views.CustomUserPasswordResetTest.test_confirm_valid_custom_user",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_default",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_guest",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_permission_required_logged_in",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_permission_required_not_logged_in",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_redirect",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_redirect_loop",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_redirect_param",  # noqa
            "auth_tests.test_views.LoginRedirectAuthenticatedUser.test_redirect_url",  # noqa
            "auth_tests.test_views.LoginRedirectUrlTest.test_custom",  # noqa
            "auth_tests.test_views.LoginRedirectUrlTest.test_default",  # noqa
            "auth_tests.test_views.LoginRedirectUrlTest.test_named",  # noqa
            "auth_tests.test_views.LoginRedirectUrlTest.test_remote",  # noqa
            "auth_tests.test_views.LoginSuccessURLAllowedHostsTest.test_success_url_allowed_hosts_safe_host",  # noqa
            "auth_tests.test_views.LoginSuccessURLAllowedHostsTest.test_success_url_allowed_hosts_same_host",  # noqa
            "auth_tests.test_views.LoginSuccessURLAllowedHostsTest.test_success_url_allowed_hosts_unsafe_host",  # noqa
            "auth_tests.test_views.LoginTest.test_current_site_in_context_after_login",  # noqa
            "auth_tests.test_views.LoginTest.test_login_csrf_rotate",  # noqa
            "auth_tests.test_views.LoginTest.test_login_form_contains_request",  # noqa
            "auth_tests.test_views.LoginTest.test_login_session_without_hash_session_key",  # noqa
            "auth_tests.test_views.LoginTest.test_security_check",  # noqa
            "auth_tests.test_views.LoginTest.test_security_check_https",  # noqa
            "auth_tests.test_views.LoginTest.test_session_key_flushed_on_login",  # noqa
            "auth_tests.test_views.LoginTest.test_session_key_flushed_on_login_after_password_change",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_https_login_url",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_lazy_login_url",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_login_url_with_querystring",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_named_login_url",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_remote_login_url",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_remote_login_url_with_next_querystring",  # noqa
            "auth_tests.test_views.LoginURLSettings.test_standard_login_url",  # noqa
            "auth_tests.test_views.LogoutTest.test_14377",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_default",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_doesnt_cache",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_preserve_language",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_redirect_url_named_setting",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_redirect_url_setting",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_custom_redirect_argument",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_named_redirect",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_next_page_specified",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_overridden_redirect_url",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_post",  # noqa
            "auth_tests.test_views.LogoutTest.test_logout_with_redirect_argument",  # noqa
            "auth_tests.test_views.LogoutTest.test_security_check",  # noqa
            "auth_tests.test_views.LogoutTest.test_security_check_https",  # noqa
            "auth_tests.test_views.LogoutTest.test_success_url_allowed_hosts_safe_host",  # noqa
            "auth_tests.test_views.LogoutTest.test_success_url_allowed_hosts_same_host",  # noqa
            "auth_tests.test_views.LogoutTest.test_success_url_allowed_hosts_unsafe_host",  # noqa
            "auth_tests.test_views.LogoutThenLoginTests.test_default_logout_then_login",  # noqa
            "auth_tests.test_views.LogoutThenLoginTests.test_logout_then_login_with_custom_login",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_complete",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_custom_reset_url_token",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_custom_reset_url_token_link_redirects_to_set_password_page",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_different_passwords",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_display_user_from_form",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_invalid",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_invalid_hash",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_invalid_post",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_invalid_user",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_link_redirects_to_set_password_page",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_login_post_reset",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_login_post_reset_already_logged_in",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_login_post_reset_custom_backend",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_overflow_user",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_redirect_custom",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_redirect_custom_named",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_redirect_default",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_confirm_valid",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_email_found",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_email_found_custom_from",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_email_not_found",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_extra_email_context",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_html_mail_template",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_invalid_link_if_going_directly_to_the_final_reset_password_url",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_poisoned_http_host",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_poisoned_http_host_admin_site",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_reset_custom_redirect",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_reset_custom_redirect_named",  # noqa
            "auth_tests.test_views.PasswordResetTest.test_reset_redirect_default",  # noqa
            "auth_tests.test_views.RedirectToLoginTests.test_redirect_to_login_with_lazy",  # noqa
            "auth_tests.test_views.RedirectToLoginTests.test_redirect_to_login_with_lazy_and_unicode",  # noqa
            "auth_tests.test_views.SessionAuthenticationTests.test_user_password_change_updates_session",  # noqa
            "auth_tests.test_views.UUIDUserPasswordResetTest.test_confirm_invalid_uuid",  # noqa
            "auth_tests.test_views.UUIDUserPasswordResetTest.test_confirm_valid_custom_user",  # noqa
            "auth_tests.test_views.UUIDUserTests.test_admin_password_change",  # noqa
            "backends.tests.FkConstraintsTests.test_disable_constraint_checks_context_manager",  # noqa
            "backends.tests.FkConstraintsTests.test_disable_constraint_checks_manually",  # noqa
            "backends.tests.FkConstraintsTests.test_integrity_checks_on_creation",  # noqa
            "backends.tests.FkConstraintsTests.test_integrity_checks_on_update",  # noqa
            "basic.tests.ModelRefreshTests.test_lookup_in_fields",
            "basic.tests.ModelRefreshTests.test_prefetched_cache_cleared",
            "basic.tests.ModelRefreshTests.test_refresh_fk",
            "basic.tests.ModelRefreshTests.test_refresh_fk_on_delete_set_null",
            "basic.tests.ModelRefreshTests.test_refresh_null_fk",
            "basic.tests.ModelRefreshTests.test_unknown_kwarg",
            "basic.tests.ModelTest.test_ticket_20278",
            "bulk_create.tests.BulkCreateTests.test_bulk_insert_nullable_fields",  # noqa
            # Check constraints are not supported by Spanner emulator.
            "constraints.tests.CheckConstraintTests.test_abstract_name",  # noqa
            # Check constraints are not supported by Spanner emulator.
            "constraints.tests.CheckConstraintTests.test_database_constraint",  # noqa
            "constraints.tests.CheckConstraintTests.test_database_constraint_unicode",  # noqa
            "constraints.tests.CheckConstraintTests.test_name",  # noqa
            "custom_lookups.tests.SubqueryTransformTests.test_subquery_usage",  # noqa
            "custom_pk.tests.CustomPKTests.test_required_pk",  # noqa
            "custom_pk.tests.CustomPKTests.test_unique_pk",  # noqa
            "datatypes.tests.DataTypesTestCase.test_boolean_type",  # noqa
            "datatypes.tests.DataTypesTestCase.test_date_type",  # noqa
            "datatypes.tests.DataTypesTestCase.test_textfields_str",  # noqa
            "datatypes.tests.DataTypesTestCase.test_time_field",  # noqa
            "datatypes.tests.DataTypesTestCase.test_year_boundaries",  # noqa
            "dates.tests.DatesTests.test_related_model_traverse",  # noqa
            "datetimes.tests.DateTimesTests.test_datetimes_ambiguous_and_invalid_times",  # noqa
            "datetimes.tests.DateTimesTests.test_datetimes_has_lazy_iterator",  # noqa
            "datetimes.tests.DateTimesTests.test_datetimes_returns_available_dates_for_given_scope_and_given_field",  # noqa
            "datetimes.tests.DateTimesTests.test_related_model_traverse",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_date",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_date_group_by",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_db_datetime_to_time",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_field",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_python",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_python_to_date",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_python_to_datetime",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_from_value",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_to_char_field_with_max_length",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_to_char_field_without_max_length",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_to_duration",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_to_integer",  # noqa
            "db_functions.comparison.test_cast.CastTests.test_cast_to_text_field",  # noqa
            "db_functions.comparison.test_coalesce.CoalesceTests.test_basic",  # noqa
            "db_functions.comparison.test_coalesce.CoalesceTests.test_mixed_values",  # noqa
            "db_functions.comparison.test_coalesce.CoalesceTests.test_ordering",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_all_null",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_basic",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_coalesce_workaround",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_propagates_null",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_related_field",  # noqa
            "db_functions.comparison.test_greatest.GreatestTests.test_update",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_all_null",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_basic",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_coalesce_workaround",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_propagates_null",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_related_field",  # noqa
            "db_functions.comparison.test_least.LeastTests.test_update",  # noqa
            "db_functions.comparison.test_nullif.NullIfTests.test_basic",  # noqa
            "db_functions.comparison.test_nullif.NullIfTests.test_null_argument",  # noqa
            "db_functions.comparison.test_nullif.NullIfTests.test_too_few_args",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_extract_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_date_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_subquery_with_parameters",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_time_func",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionTests.test_trunc_time_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_extract_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_date_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_none",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_subquery_with_parameters",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_time_func",  # noqa
            "db_functions.datetime.test_extract_trunc.DateFunctionWithTimeZoneTests.test_trunc_time_none",  # noqa
            "db_functions.datetime.test_now.NowTests.test_basic",  # noqa
            "db_functions.math.test_abs.AbsTests.test_null",  # noqa
            "db_functions.math.test_acos.ACosTests.test_null",  # noqa
            "db_functions.math.test_asin.ASinTests.test_null",  # noqa
            "db_functions.math.test_atan.ATanTests.test_null",  # noqa
            "db_functions.math.test_atan2.ATan2Tests.test_null",  # noqa
            "db_functions.math.test_ceil.CeilTests.test_decimal",  # noqa
            "db_functions.math.test_ceil.CeilTests.test_float",  # noqa
            "db_functions.math.test_ceil.CeilTests.test_integer",  # noqa
            "db_functions.math.test_ceil.CeilTests.test_null",  # noqa
            "db_functions.math.test_ceil.CeilTests.test_transform",  # noqa
            "db_functions.math.test_cos.CosTests.test_null",  # noqa
            "db_functions.math.test_cos.CosTests.test_transform",  # noqa
            "db_functions.math.test_cot.CotTests.test_null",  # noqa
            "db_functions.math.test_degrees.DegreesTests.test_decimal",  # noqa
            "db_functions.math.test_degrees.DegreesTests.test_null",  # noqa
            "db_functions.math.test_exp.ExpTests.test_decimal",  # noqa
            "db_functions.math.test_exp.ExpTests.test_null",  # noqa
            "db_functions.math.test_exp.ExpTests.test_transform",  # noqa
            "db_functions.math.test_floor.FloorTests.test_null",  # noqa
            "db_functions.math.test_ln.LnTests.test_decimal",  # noqa
            "db_functions.math.test_ln.LnTests.test_null",  # noqa
            "db_functions.math.test_ln.LnTests.test_transform",  # noqa
            "db_functions.math.test_log.LogTests.test_decimal",  # noqa
            "db_functions.math.test_log.LogTests.test_null",  # noqa
            "db_functions.math.test_mod.ModTests.test_float",  # noqa
            "db_functions.math.test_mod.ModTests.test_null",  # noqa
            "db_functions.math.test_power.PowerTests.test_decimal",  # noqa
            "db_functions.math.test_power.PowerTests.test_float",  # noqa
            "db_functions.math.test_power.PowerTests.test_integer",  # noqa
            "db_functions.math.test_power.PowerTests.test_null",  # noqa
            "db_functions.math.test_radians.RadiansTests.test_null",  # noqa
            "db_functions.math.test_round.RoundTests.test_null",  # noqa
            "db_functions.math.test_sin.SinTests.test_null",  # noqa
            "db_functions.math.test_sqrt.SqrtTests.test_decimal",  # noqa
            "db_functions.math.test_sqrt.SqrtTests.test_null",  # noqa
            "db_functions.math.test_sqrt.SqrtTests.test_transform",  # noqa
            "db_functions.math.test_tan.TanTests.test_null",  # noqa
            "db_functions.tests.FunctionTests.test_func_transform_bilateral",  # noqa
            "db_functions.tests.FunctionTests.test_func_transform_bilateral_multivalue",  # noqa
            "db_functions.tests.FunctionTests.test_function_as_filter",  # noqa
            "db_functions.tests.FunctionTests.test_nested_function_ordering",  # noqa
            "db_functions.text.test_chr.ChrTests.test_basic",  # noqa
            "db_functions.text.test_chr.ChrTests.test_non_ascii",  # noqa
            "db_functions.text.test_chr.ChrTests.test_transform",  # noqa
            "db_functions.text.test_concat.ConcatTests.test_basic",  # noqa
            "db_functions.text.test_concat.ConcatTests.test_many",  # noqa
            "db_functions.text.test_concat.ConcatTests.test_mixed_char_text",  # noqa
            "db_functions.text.test_left.LeftTests.test_basic",  # noqa
            "db_functions.text.test_left.LeftTests.test_expressions",  # noqa
            "db_functions.text.test_left.LeftTests.test_invalid_length",  # noqa
            "db_functions.text.test_length.LengthTests.test_basic",  # noqa
            "db_functions.text.test_length.LengthTests.test_ordering",  # noqa
            "db_functions.text.test_length.LengthTests.test_transform",  # noqa
            "db_functions.text.test_lower.LowerTests.test_basic",  # noqa
            "db_functions.text.test_lower.LowerTests.test_transform",  # noqa
            "db_functions.text.test_ord.OrdTests.test_basic",  # noqa
            "db_functions.text.test_ord.OrdTests.test_transform",  # noqa
            "db_functions.text.test_pad.PadTests.test_combined_with_length",  # noqa
            "db_functions.text.test_pad.PadTests.test_pad",  # noqa
            "db_functions.text.test_repeat.RepeatTests.test_basic",  # noqa
            "db_functions.text.test_replace.ReplaceTests.test_case_sensitive",  # noqa
            "db_functions.text.test_replace.ReplaceTests.test_replace_expression",  # noqa
            "db_functions.text.test_replace.ReplaceTests.test_replace_with_default_arg",  # noqa
            "db_functions.text.test_replace.ReplaceTests.test_replace_with_empty_string",  # noqa
            "db_functions.text.test_replace.ReplaceTests.test_update",  # noqa
            "db_functions.text.test_reverse.ReverseTests.test_basic",  # noqa
            "db_functions.text.test_reverse.ReverseTests.test_expressions",  # noqa
            "db_functions.text.test_reverse.ReverseTests.test_null",  # noqa
            "db_functions.text.test_reverse.ReverseTests.test_transform",  # noqa
            "db_functions.text.test_right.RightTests.test_basic",  # noqa
            "db_functions.text.test_right.RightTests.test_expressions",  # noqa
            "db_functions.text.test_right.RightTests.test_invalid_length",  # noqa
            "db_functions.text.test_strindex.StrIndexTests.test_annotate_charfield",  # noqa
            "db_functions.text.test_strindex.StrIndexTests.test_annotate_textfield",  # noqa
            "db_functions.text.test_strindex.StrIndexTests.test_filtering",  # noqa
            "db_functions.text.test_strindex.StrIndexTests.test_order_by",  # noqa
            "db_functions.text.test_strindex.StrIndexTests.test_unicode_values",  # noqa
            "db_functions.text.test_substr.SubstrTests.test_basic",  # noqa
            "db_functions.text.test_substr.SubstrTests.test_expressions",  # noqa
            "db_functions.text.test_substr.SubstrTests.test_start",  # noqa
            "db_functions.text.test_trim.TrimTests.test_trim",  # noqa
            "db_functions.text.test_trim.TrimTests.test_trim_transform",  # noqa
            "db_functions.text.test_upper.UpperTests.test_basic",  # noqa
            "db_functions.text.test_upper.UpperTests.test_transform",  # noqa
            "delete_regress.tests.DeleteCascadeTransactionTests.test_inheritance",  # noqa
            "delete_regress.tests.DeleteLockingTest.test_concurrent_delete",  # noqa
            "expressions.test_queryset_values.ValuesExpressionsTests.test_chained_values_with_expression",  # noqa
            "expressions.test_queryset_values.ValuesExpressionsTests.test_values_expression",  # noqa
            "expressions.test_queryset_values.ValuesExpressionsTests.test_values_expression_group_by",  # noqa
            "expressions.test_queryset_values.ValuesExpressionsTests.test_values_list_expression",  # noqa
            "expressions.test_queryset_values.ValuesExpressionsTests.test_values_list_expression_flat",  # noqa
            "expressions.tests.BasicExpressionsTests.test_annotate_values_aggregate",  # noqa
            "expressions.tests.BasicExpressionsTests.test_annotate_values_filter",  # noqa
            "expressions.tests.BasicExpressionsTests.test_annotations_within_subquery",  # noqa
            "expressions.tests.BasicExpressionsTests.test_arithmetic",  # noqa
            "expressions.tests.BasicExpressionsTests.test_exist_single_field_output_field",  # noqa
            "expressions.tests.BasicExpressionsTests.test_explicit_output_field",  # noqa
            "expressions.tests.BasicExpressionsTests.test_filter_inter_attribute",  # noqa
            "expressions.tests.BasicExpressionsTests.test_filter_with_join",  # noqa
            "expressions.tests.BasicExpressionsTests.test_in_subquery",  # noqa
            "expressions.tests.BasicExpressionsTests.test_incorrect_field_in_F_expression",  # noqa
            "expressions.tests.BasicExpressionsTests.test_incorrect_joined_field_in_F_expression",  # noqa
            "expressions.tests.BasicExpressionsTests.test_nested_subquery",  # noqa
            "expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_2",  # noqa
            "expressions.tests.BasicExpressionsTests.test_nested_subquery_outer_ref_with_autofield",  # noqa
            "expressions.tests.BasicExpressionsTests.test_new_object_create",  # noqa
            "expressions.tests.BasicExpressionsTests.test_new_object_save",  # noqa
            "expressions.tests.BasicExpressionsTests.test_object_create_with_aggregate",  # noqa
            "expressions.tests.BasicExpressionsTests.test_object_update",  # noqa
            "expressions.tests.BasicExpressionsTests.test_object_update_fk",  # noqa
            "expressions.tests.BasicExpressionsTests.test_object_update_unsaved_objects",  # noqa
            "expressions.tests.BasicExpressionsTests.test_order_by_exists",  # noqa
            "expressions.tests.BasicExpressionsTests.test_order_of_operations",  # noqa
            "expressions.tests.BasicExpressionsTests.test_outerref",  # noqa
            "expressions.tests.BasicExpressionsTests.test_outerref_with_operator",  # noqa
            "expressions.tests.BasicExpressionsTests.test_parenthesis_priority",  # noqa
            "expressions.tests.BasicExpressionsTests.test_pickle_expression",  # noqa
            "expressions.tests.BasicExpressionsTests.test_subquery",  # noqa
            "expressions.tests.BasicExpressionsTests.test_subquery_filter_by_aggregate",  # noqa
            "expressions.tests.BasicExpressionsTests.test_subquery_references_joined_table_twice",  # noqa
            "expressions.tests.BasicExpressionsTests.test_ticket_11722_iexact_lookup",  # noqa
            "expressions.tests.BasicExpressionsTests.test_ticket_18375_chained_filters",  # noqa
            "expressions.tests.BasicExpressionsTests.test_ticket_18375_join_reuse",  # noqa
            "expressions.tests.BasicExpressionsTests.test_ticket_18375_kwarg_ordering",  # noqa
            "expressions.tests.BasicExpressionsTests.test_ticket_18375_kwarg_ordering_2",  # noqa
            "expressions.tests.BasicExpressionsTests.test_update",  # noqa
            "expressions.tests.BasicExpressionsTests.test_update_inherited_field_value",  # noqa
            "expressions.tests.BasicExpressionsTests.test_update_with_fk",  # noqa
            "expressions.tests.BasicExpressionsTests.test_update_with_none",  # noqa
            "expressions.tests.BasicExpressionsTests.test_uuid_pk_subquery",  # noqa
            "expressions.tests.ExpressionsNumericTests.test_complex_expressions",  # noqa
            "expressions.tests.ExpressionsNumericTests.test_fill_with_value_from_same_object",  # noqa
            "expressions.tests.ExpressionsNumericTests.test_filter_not_equals_other_field",  # noqa
            "expressions.tests.ExpressionsNumericTests.test_increment_value",  # noqa
            "expressions.tests.ExpressionsTests.test_F_reuse",  # noqa
            "expressions.tests.IterableLookupInnerExpressionsTests.test_expressions_in_lookups_join_choice",  # noqa
            "expressions.tests.IterableLookupInnerExpressionsTests.test_in_lookup_allows_F_expressions_and_expressions_for_datetimes",  # noqa
            "expressions.tests.IterableLookupInnerExpressionsTests.test_in_lookup_allows_F_expressions_and_expressions_for_integers",  # noqa
            "expressions.tests.IterableLookupInnerExpressionsTests.test_range_lookup_allows_F_expressions_and_expressions_for_integers",  # noqa
            "expressions.tests.ValueTests.test_update_TimeField_using_Value",  # noqa
            "expressions.tests.ValueTests.test_update_UUIDField_using_Value",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_ambiguous_compressed_fixture",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_dumpdata_progressbar",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_dumpdata_with_file_output",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_dumpdata_with_pks",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_loaddata_error_message",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_loaddata_verbosity_three",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_loading_and_dumping",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_loading_stdin",  # noqa
            "fixtures.tests.FixtureLoadingTests.test_output_formats",  # noqa
            "fixtures.tests.FixtureTransactionTests.test_format_discovery",  # noqa
            "fixtures.tests.ForwardReferenceTests.test_forward_reference_fk",  # noqa
            "fixtures.tests.ForwardReferenceTests.test_forward_reference_m2m",  # noqa
            "fixtures.tests.TestCaseFixtureLoadingTests.test_class_fixtures",  # noqa
            "fixtures_model_package.tests.FixtureTestCase.test_loaddata",  # noqa
            "flatpages_tests.test_csrf.FlatpageCSRFTests.test_view_authenticated_flatpage",  # noqa
            "flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_fallback_authenticated_flatpage",  # noqa
            "flatpages_tests.test_middleware.FlatpageMiddlewareTests.test_view_authenticated_flatpage",  # noqa
            "flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_tag_for_user",  # noqa
            "flatpages_tests.test_templatetags.FlatpageTemplateTagTests.test_get_flatpages_with_prefix_for_user",  # noqa
            "flatpages_tests.test_views.FlatpageViewTests.test_view_authenticated_flatpage",  # noqa
            "force_insert_update.tests.InheritanceTests.test_force_update_on_inherited_model",  # noqa
            "force_insert_update.tests.InheritanceTests.test_force_update_on_inherited_model_without_fields",  # noqa
            "foreign_object.tests.MultiColumnFKTests.test_translations",  # noqa
            "generic_inline_admin.tests.GenericAdminViewTest.test_basic_add_GET",  # noqa
            "generic_inline_admin.tests.GenericAdminViewTest.test_basic_add_POST",  # noqa
            "generic_inline_admin.tests.GenericAdminViewTest.test_basic_edit_GET",  # noqa
            "generic_inline_admin.tests.GenericAdminViewTest.test_basic_edit_POST",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_extra_param",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_get_extra",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_get_max_num",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_get_min_num",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_max_num_param",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_min_num_param",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminParametersTest.test_no_param",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminWithUniqueTogetherTest.test_add",  # noqa
            "generic_inline_admin.tests.GenericInlineAdminWithUniqueTogetherTest.test_delete",  # noqa
            "get_or_create.tests.GetOrCreateTests.test_get_or_create_invalid_params",  # noqa
            "get_or_create.tests.GetOrCreateTestsWithManualPKs.test_create_with_duplicate_primary_key",  # noqa
            "get_or_create.tests.GetOrCreateTestsWithManualPKs.test_get_or_create_raises_IntegrityError_plus_traceback",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_create_twice",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_defaults_exact",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_update",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_update_callable_default",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_update_with_many",  # noqa
            "get_or_create.tests.UpdateOrCreateTests.test_update_with_related_manager",  # noqa
            "i18n.tests.WatchForTranslationChangesTests.test_i18n_app_dirs",  # noqa
            # Emulator doesn't support views.
            "inspectdb.tests.InspectDBTransactionalTests.test_include_views",
            "introspection.tests.IntrospectionTests.test_get_constraints",  # noqa
            "introspection.tests.IntrospectionTests.test_get_constraints_index_types",  # noqa
            "introspection.tests.IntrospectionTests.test_get_constraints_indexes_orders",  # noqa
            "introspection.tests.IntrospectionTests.test_get_primary_key_column",  # noqa
            "introspection.tests.IntrospectionTests.test_table_names_with_views",
            "lookup.tests.LookupTests.test_custom_field_none_rhs",  # noqa
            "lookup.tests.LookupTests.test_custom_lookup_none_rhs",  # noqa
            "lookup.tests.LookupTests.test_escaping",  # noqa
            "lookup.tests.LookupTests.test_exact_none_transform",  # noqa
            "lookup.tests.LookupTests.test_exclude",  # noqa
            "lookup.tests.LookupTests.test_in_bulk_lots_of_ids",  # noqa
            "lookup.tests.LookupTests.test_lookup_collision",  # noqa
            "lookup.tests.LookupTests.test_regex",  # noqa
            "lookup.tests.LookupTests.test_regex_non_string",  # noqa
            "lookup.tests.LookupTests.test_regex_null",  # noqa
            "m2m_through.tests.M2mThroughReferentialTests.test_through_fields_self_referential",  # noqa
            "m2m_through.tests.M2mThroughTests.test_add_on_m2m_with_intermediate_model_value_required_fails",  # noqa
            "m2m_through.tests.M2mThroughTests.test_add_on_reverse_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_clear_on_reverse_removes_all_the_m2m_relationships",  # noqa
            "m2m_through.tests.M2mThroughTests.test_clear_removes_all_the_m2m_relationships",  # noqa
            "m2m_through.tests.M2mThroughTests.test_create_on_m2m_with_intermediate_model_value_required_fails",  # noqa
            "m2m_through.tests.M2mThroughTests.test_create_on_reverse_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_custom_related_name_doesnt_conflict_with_fky_related_name",  # noqa
            "m2m_through.tests.M2mThroughTests.test_custom_related_name_forward_non_empty_qs",  # noqa
            "m2m_through.tests.M2mThroughTests.test_custom_related_name_reverse_non_empty_qs",  # noqa
            "m2m_through.tests.M2mThroughTests.test_filter_on_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_get_on_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_get_or_create_on_m2m_with_intermediate_model_value_required_fails",  # noqa
            "m2m_through.tests.M2mThroughTests.test_order_by_relational_field_through_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_first_model_by_intermediate_model_attribute",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_model_by_attribute_name_of_related_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_model_by_custom_related_name",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_model_by_intermediate_can_return_non_unique_queryset",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_model_by_related_model_name",  # noqa
            "m2m_through.tests.M2mThroughTests.test_query_second_model_by_intermediate_model_attribute",  # noqa
            "m2m_through.tests.M2mThroughTests.test_remove_on_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_remove_on_reverse_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_retrieve_intermediate_items",  # noqa
            "m2m_through.tests.M2mThroughTests.test_retrieve_reverse_intermediate_items",  # noqa
            "m2m_through.tests.M2mThroughTests.test_set_on_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_set_on_m2m_with_intermediate_model_value_required_fails",  # noqa
            "m2m_through.tests.M2mThroughTests.test_set_on_reverse_m2m_with_intermediate_model",  # noqa
            "m2m_through.tests.M2mThroughTests.test_update_or_create_on_m2m_with_intermediate_model_value_required_fails",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_join_trimming_forwards",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_join_trimming_reverse",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_retrieve_forward_m2m_items",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_retrieve_forward_m2m_items_via_custom_id_intermediary",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_retrieve_reverse_m2m_items",  # noqa
            "m2m_through_regress.tests.M2MThroughTestCase.test_retrieve_reverse_m2m_items_via_custom_id_intermediary",  # noqa
            "m2m_through_regress.tests.ThroughLoadDataTestCase.test_sequence_creation",  # noqa
            "m2m_through_regress.tests.ToFieldThroughTests.test_add_null_reverse",  # noqa
            "m2m_through_regress.tests.ToFieldThroughTests.test_add_null_reverse_related",  # noqa
            "m2m_through_regress.tests.ToFieldThroughTests.test_add_related_null",  # noqa
            "m2o_recursive.tests.ManyToOneRecursiveTests.test_m2o_recursive",  # noqa
            "m2o_recursive.tests.MultipleManyToOneRecursiveTests.test_m2o_recursive2",  # noqa
            "managers_regress.tests.ManagersRegressionTests.test_field_can_be_called_exact",  # noqa
            "managers_regress.tests.ManagersRegressionTests.test_regress_3871",  # noqa
            "many_to_one.tests.ManyToOneTests.test_add_after_prefetch",  # noqa
            "many_to_one.tests.ManyToOneTests.test_add_then_remove_after_prefetch",  # noqa
            "many_to_one.tests.ManyToOneTests.test_cached_foreign_key_with_to_field_not_cleared_by_save",  # noqa
            "many_to_one.tests.ManyToOneTests.test_reverse_foreign_key_instance_to_field_caching",  # noqa
            "many_to_one.tests.ManyToOneTests.test_set_after_prefetch",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_add_efficiency",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_assign_clear_related_set",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_assign_with_queryset",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_clear_efficiency",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_created_via_related_set",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_created_without_related",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_get_related",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_related_null_to_field",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_related_set",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_remove_from_wrong_set",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_set",  # noqa
            "many_to_one_null.tests.ManyToOneNullTests.test_set_clear_non_bulk",  # noqa
            "migrations.test_operations.OperationTests.test_add_binaryfield",  # noqa
            "migrations.test_operations.OperationTests.test_add_charfield",  # noqa
            "migrations.test_operations.OperationTests.test_add_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_add_constraint_percent_escaping",  # noqa
            "migrations.test_operations.OperationTests.test_add_field",  # noqa
            "migrations.test_operations.OperationTests.test_add_field_m2m",  # noqa
            "migrations.test_operations.OperationTests.test_add_field_preserve_default",  # noqa
            "migrations.test_operations.OperationTests.test_add_index",  # noqa
            "migrations.test_operations.OperationTests.test_add_index_state_forwards",  # noqa
            "migrations.test_operations.OperationTests.test_add_or_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_add_partial_unique_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_add_textfield",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field_m2m",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field_pk",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field_pk_fk",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_target_changes",  # noqa
            "migrations.test_operations.OperationTests.test_alter_field_reloads_state_on_fk_with_to_field_target_changes",  # noqa
            "migrations.test_operations.OperationTests.test_alter_fk",  # noqa
            "migrations.test_operations.OperationTests.test_alter_index_together",  # noqa
            "migrations.test_operations.OperationTests.test_alter_index_together_remove",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_managers",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_managers_emptying",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_options",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_options_emptying",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_table_none",  # noqa
            "migrations.test_operations.OperationTests.test_alter_model_table_noop",  # noqa
            "migrations.test_operations.OperationTests.test_alter_unique_together",  # noqa
            "migrations.test_operations.OperationTests.test_alter_unique_together_remove",  # noqa
            "migrations.test_operations.OperationTests.test_column_name_quoting",  # noqa
            "migrations.test_operations.OperationTests.test_create_model",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_inheritance",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_m2m",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_managers",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_duplicate_base",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_duplicate_field_name",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_duplicate_manager_name",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_partial_unique_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_create_model_with_unique_after",  # noqa
            "migrations.test_operations.OperationTests.test_create_proxy_model",  # noqa
            "migrations.test_operations.OperationTests.test_create_unmanaged_model",  # noqa
            "migrations.test_operations.OperationTests.test_delete_model",  # noqa
            "migrations.test_operations.OperationTests.test_delete_mti_model",  # noqa
            "migrations.test_operations.OperationTests.test_delete_proxy_model",  # noqa
            "migrations.test_operations.OperationTests.test_model_with_bigautofield",  # noqa
            "migrations.test_operations.OperationTests.test_remove_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_remove_field",  # noqa
            "migrations.test_operations.OperationTests.test_remove_field_m2m",  # noqa
            "migrations.test_operations.OperationTests.test_remove_field_m2m_with_through",  # noqa
            "migrations.test_operations.OperationTests.test_remove_fk",  # noqa
            "migrations.test_operations.OperationTests.test_remove_index",  # noqa
            "migrations.test_operations.OperationTests.test_remove_index_state_forwards",  # noqa
            "migrations.test_operations.OperationTests.test_remove_partial_unique_constraint",  # noqa
            "migrations.test_operations.OperationTests.test_rename_missing_field",  # noqa
            "migrations.test_operations.OperationTests.test_rename_model_state_forwards",  # noqa
            "migrations.test_operations.OperationTests.test_rename_referenced_field_state_forward",  # noqa
            "migrations.test_operations.OperationTests.test_run_python",  # noqa
            "migrations.test_operations.OperationTests.test_run_python_atomic",  # noqa
            "migrations.test_operations.OperationTests.test_run_python_noop",  # noqa
            "migrations.test_operations.OperationTests.test_run_python_related_assignment",  # noqa
            "migrations.test_operations.OperationTests.test_run_sql",  # noqa
            "migrations.test_operations.OperationTests.test_run_sql_noop",  # noqa
            "migrations.test_operations.OperationTests.test_run_sql_params_invalid",  # noqa
            "migrations.test_operations.OperationTests.test_separate_database_and_state",  # noqa
            "migrations.test_operations.OperationTests.test_separate_database_and_state2",  # noqa
            "model_fields.test_booleanfield.BooleanFieldTests.test_null_default",  # noqa
            "model_fields.test_durationfield.TestSaveLoad.test_create_empty",  # noqa
            "model_fields.test_genericipaddressfield.GenericIPAddressFieldTests.test_blank_string_saved_as_null",  # noqa
            "model_fields.test_genericipaddressfield.GenericIPAddressFieldTests.test_null_value",  # noqa
            "model_fields.test_imagefield.TwoImageFieldTests.test_dimensions",  # noqa
            "model_fields.test_imagefield.TwoImageFieldTests.test_field_save_and_delete_methods",  # noqa
            "model_fields.test_integerfield.BigIntegerFieldTests.test_backend_range_save",  # noqa
            "model_fields.test_integerfield.BigIntegerFieldTests.test_coercing",  # noqa
            "model_fields.test_integerfield.BigIntegerFieldTests.test_documented_range",  # noqa
            "model_fields.test_integerfield.BigIntegerFieldTests.test_types",  # noqa
            "model_fields.test_uuid.TestQuerying.test_exact",  # noqa
            "model_fields.test_uuid.TestQuerying.test_isnull",  # noqa
            "model_fields.test_uuid.TestSaveLoad.test_null_handling",  # noqa
            "model_inheritance.tests.ModelInheritanceDataTests.test_update_inherited_model",  # noqa
            "model_inheritance.tests.ModelInheritanceDataTests.test_update_query_counts",  # noqa
            "model_inheritance.tests.ModelInheritanceTests.test_update_parent_filtering",  # noqa
            "model_inheritance_regress.tests.ModelInheritanceTest.test_id_field_update_on_ancestor_change",  # noqa
            "model_inheritance_regress.tests.ModelInheritanceTest.test_model_inheritance",  # noqa
            "multiple_database.tests.FixtureTestCase.test_fixture_loading",  # noqa
            "multiple_database.tests.FixtureTestCase.test_pseudo_empty_fixtures",  # noqa
            "multiple_database.tests.PickleQuerySetTestCase.test_pickling",  # noqa
            "multiple_database.tests.QueryTestCase.test_basic_queries",  # noqa
            "multiple_database.tests.QueryTestCase.test_default_creation",  # noqa
            "multiple_database.tests.QueryTestCase.test_foreign_key_cross_database_protection",  # noqa
            "multiple_database.tests.QueryTestCase.test_foreign_key_reverse_operations",  # noqa
            "multiple_database.tests.QueryTestCase.test_foreign_key_separation",  # noqa
            "multiple_database.tests.QueryTestCase.test_generic_key_cross_database_protection",  # noqa
            "multiple_database.tests.QueryTestCase.test_generic_key_deletion",  # noqa
            "multiple_database.tests.QueryTestCase.test_generic_key_reverse_operations",  # noqa
            "multiple_database.tests.QueryTestCase.test_generic_key_separation",  # noqa
            "multiple_database.tests.QueryTestCase.test_m2m_cross_database_protection",  # noqa
            "multiple_database.tests.QueryTestCase.test_m2m_deletion",  # noqa
            "multiple_database.tests.QueryTestCase.test_m2m_forward_operations",  # noqa
            "multiple_database.tests.QueryTestCase.test_m2m_reverse_operations",  # noqa
            "multiple_database.tests.QueryTestCase.test_m2m_separation",  # noqa
            "multiple_database.tests.QueryTestCase.test_o2o_cross_database_protection",  # noqa
            "multiple_database.tests.QueryTestCase.test_o2o_separation",  # noqa
            "multiple_database.tests.QueryTestCase.test_ordering",  # noqa
            "multiple_database.tests.QueryTestCase.test_other_creation",  # noqa
            "multiple_database.tests.QueryTestCase.test_raw",  # noqa
            "multiple_database.tests.QueryTestCase.test_refresh",  # noqa
            "multiple_database.tests.QueryTestCase.test_refresh_router_instance_hint",  # noqa
            "multiple_database.tests.QueryTestCase.test_related_manager",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_add",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_clear",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_delete",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_get_or_create",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_remove",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_m2m_update",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_add",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_clear",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_delete",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_get_or_create",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_remove",  # noqa
            "multiple_database.tests.RouteForWriteTestCase.test_reverse_m2m_update",  # noqa
            "multiple_database.tests.RouterAttributeErrorTestCase.test_attribute_error_delete",  # noqa
            "multiple_database.tests.RouterAttributeErrorTestCase.test_attribute_error_m2m",  # noqa
            "multiple_database.tests.RouterAttributeErrorTestCase.test_attribute_error_read",  # noqa
            "multiple_database.tests.RouterModelArgumentTestCase.test_m2m_collection",  # noqa
            "multiple_database.tests.RouterTestCase.test_database_routing",  # noqa
            "multiple_database.tests.RouterTestCase.test_foreign_key_cross_database_protection",  # noqa
            "multiple_database.tests.RouterTestCase.test_generic_key_managers",  # noqa
            "multiple_database.tests.RouterTestCase.test_invalid_set_foreign_key_assignment",  # noqa
            "multiple_database.tests.RouterTestCase.test_m2m_cross_database_protection",  # noqa
            "multiple_database.tests.RouterTestCase.test_m2m_managers",  # noqa
            "multiple_database.tests.RouterTestCase.test_o2o_cross_database_protection",  # noqa
            "multiple_database.tests.RouterTestCase.test_partial_router",  # noqa
            "multiple_database.tests.SignalTests.test_database_arg_m2m",  # noqa
            "null_fk.tests.NullFkTests.test_combine_isnull",  # noqa
            "null_fk.tests.NullFkTests.test_null_fk",  # noqa
            "null_fk_ordering.tests.NullFkOrderingTests.test_ordering_across_null_fk",  # noqa
            "null_queries.tests.NullQueriesTests.test_reverse_relations",  # noqa
            "ordering.tests.OrderingTests.test_default_ordering",  # noqa
            "ordering.tests.OrderingTests.test_default_ordering_override",  # noqa
            "ordering.tests.OrderingTests.test_extra_ordering",  # noqa
            "ordering.tests.OrderingTests.test_extra_ordering_quoting",  # noqa
            "ordering.tests.OrderingTests.test_extra_ordering_with_table_name",  # noqa
            "ordering.tests.OrderingTests.test_no_reordering_after_slicing",  # noqa
            "ordering.tests.OrderingTests.test_order_by_f_expression",  # noqa
            "ordering.tests.OrderingTests.test_order_by_f_expression_duplicates",  # noqa
            "ordering.tests.OrderingTests.test_order_by_nulls_first",  # noqa
            "ordering.tests.OrderingTests.test_order_by_nulls_first_and_last",  # noqa
            "ordering.tests.OrderingTests.test_order_by_nulls_last",  # noqa
            "ordering.tests.OrderingTests.test_orders_nulls_first_on_filtered_subquery",  # noqa
            "ordering.tests.OrderingTests.test_related_ordering_duplicate_table_reference",  # noqa
            "ordering.tests.OrderingTests.test_reverse_ordering_pure",  # noqa
            "ordering.tests.OrderingTests.test_reversed_ordering",  # noqa
            "ordering.tests.OrderingTests.test_stop_slicing",  # noqa
            "ordering.tests.OrderingTests.test_stop_start_slicing",  # noqa
            "proxy_models.tests.ProxyModelAdminTests.test_delete_str_in_model_admin",  # noqa
            "queries.test_bulk_update.BulkUpdateNoteTests.test_batch_size",  # noqa
            "queries.test_bulk_update.BulkUpdateNoteTests.test_functions",  # noqa
            "queries.test_bulk_update.BulkUpdateNoteTests.test_set_field_to_null",  # noqa
            "queries.test_bulk_update.BulkUpdateNoteTests.test_set_mixed_fields_to_null",  # noqa
            "queries.test_bulk_update.BulkUpdateNoteTests.test_simple",  # noqa
            "queries.test_bulk_update.BulkUpdateTests.test_custom_db_columns",  # noqa
            "queries.test_bulk_update.BulkUpdateTests.test_field_references",  # noqa
            "queries.test_bulk_update.BulkUpdateTests.test_ipaddressfield",  # noqa
            "queries.tests.CloneTests.test_evaluated_queryset_as_argument",  # noqa
            "queries.tests.ComparisonTests.test_ticket8597",  # noqa
            "queries.tests.ConditionalTests.test_in_list_limit",  # noqa
            "queries.tests.ConditionalTests.test_infinite_loop",  # noqa
            "queries.tests.ConditionalTests.test_null_ordering_added",  # noqa
            "queries.tests.DisjunctionPromotionTests.test_disjunction_promotion_select_related",  # noqa
            "queries.tests.DisjunctiveFilterTests.test_ticket7872",  # noqa
            "queries.tests.DisjunctiveFilterTests.test_ticket8283",  # noqa
            "queries.tests.IsNullTests.test_primary_key",  # noqa
            "queries.tests.IsNullTests.test_to_field",  # noqa
            "queries.tests.JoinReuseTest.test_inverted_q_across_relations",  # noqa
            "queries.tests.NullInExcludeTest.test_col_not_in_list_containing_null",  # noqa
            "queries.tests.NullInExcludeTest.test_double_exclude",  # noqa
            "queries.tests.NullInExcludeTest.test_null_in_exclude_qs",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_isnull_filter_promotion",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_null_join_demotion",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_17886",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_21366",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_21748",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_21748_complex_filter",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_21748_double_negated_and",  # noqa
            "queries.tests.NullJoinPromotionOrTest.test_ticket_21748_double_negated_or",  # noqa
            "queries.tests.NullableRelOrderingTests.test_join_already_in_query",  # noqa
            "queries.tests.NullableRelOrderingTests.test_ticket10028",  # noqa
            "queries.tests.Queries1Tests.test_avoid_infinite_loop_on_too_many_subqueries",  # noqa
            "queries.tests.Queries1Tests.test_common_mixed_case_foreign_keys",  # noqa
            "queries.tests.Queries1Tests.test_deferred_load_qs_pickling",  # noqa
            "queries.tests.Queries1Tests.test_double_exclude",  # noqa
            "queries.tests.Queries1Tests.test_error_raised_on_filter_with_dictionary",  # noqa
            "queries.tests.Queries1Tests.test_exclude",  # noqa
            "queries.tests.Queries1Tests.test_exclude_in",  # noqa
            "queries.tests.Queries1Tests.test_excluded_intermediary_m2m_table_joined",  # noqa
            "queries.tests.Queries1Tests.test_field_with_filterable",  # noqa
            "queries.tests.Queries1Tests.test_get_clears_ordering",  # noqa
            "queries.tests.Queries1Tests.test_heterogeneous_qs_combination",  # noqa
            "queries.tests.Queries1Tests.test_lookup_constraint_fielderror",  # noqa
            "queries.tests.Queries1Tests.test_negate_field",  # noqa
            "queries.tests.Queries1Tests.test_nested_exclude",  # noqa
            "queries.tests.Queries1Tests.test_order_by_join_unref",  # noqa
            "queries.tests.Queries1Tests.test_order_by_rawsql",  # noqa
            "queries.tests.Queries1Tests.test_order_by_tables",  # noqa
            "queries.tests.Queries1Tests.test_reasonable_number_of_subq_aliases",  # noqa
            "queries.tests.Queries1Tests.test_subquery_condition",  # noqa
            "queries.tests.Queries1Tests.test_ticket10205",  # noqa
            "queries.tests.Queries1Tests.test_ticket10432",  # noqa
            "queries.tests.Queries1Tests.test_ticket1050",  # noqa
            "queries.tests.Queries1Tests.test_ticket10742",  # noqa
            "queries.tests.Queries1Tests.test_ticket17429",  # noqa
            "queries.tests.Queries1Tests.test_ticket1801",  # noqa
            "queries.tests.Queries1Tests.test_ticket19672",  # noqa
            "queries.tests.Queries1Tests.test_ticket2091",  # noqa
            "queries.tests.Queries1Tests.test_ticket2253",  # noqa
            "queries.tests.Queries1Tests.test_ticket2306",  # noqa
            "queries.tests.Queries1Tests.test_ticket2400",  # noqa
            "queries.tests.Queries1Tests.test_ticket2496",  # noqa
            "queries.tests.Queries1Tests.test_ticket3037",  # noqa
            "queries.tests.Queries1Tests.test_ticket3141",  # noqa
            "queries.tests.Queries1Tests.test_ticket4358",  # noqa
            "queries.tests.Queries1Tests.test_ticket4464",  # noqa
            "queries.tests.Queries1Tests.test_ticket4510",  # noqa
            "queries.tests.Queries1Tests.test_ticket6074",  # noqa
            "queries.tests.Queries1Tests.test_ticket6154",  # noqa
            "queries.tests.Queries1Tests.test_ticket6981",  # noqa
            "queries.tests.Queries1Tests.test_ticket7076",  # noqa
            "queries.tests.Queries1Tests.test_ticket7096",  # noqa
            "queries.tests.Queries1Tests.test_ticket7155",  # noqa
            "queries.tests.Queries1Tests.test_ticket7181",  # noqa
            "queries.tests.Queries1Tests.test_ticket7235",  # noqa
            "queries.tests.Queries1Tests.test_ticket7277",  # noqa
            "queries.tests.Queries1Tests.test_ticket7323",  # noqa
            "queries.tests.Queries1Tests.test_ticket7378",  # noqa
            "queries.tests.Queries1Tests.test_ticket7791",  # noqa
            "queries.tests.Queries1Tests.test_ticket7813",  # noqa
            "queries.tests.Queries1Tests.test_ticket8439",  # noqa
            "queries.tests.Queries1Tests.test_ticket9926",  # noqa
            "queries.tests.Queries1Tests.test_ticket9985",  # noqa
            "queries.tests.Queries1Tests.test_ticket9997",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_1",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_2",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_3",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_4",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_5",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_6",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_7",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_8",  # noqa
            "queries.tests.Queries1Tests.test_ticket_10790_combine",  # noqa
            "queries.tests.Queries1Tests.test_ticket_20250",  # noqa
            "queries.tests.Queries1Tests.test_tickets_1878_2939",  # noqa
            "queries.tests.Queries1Tests.test_tickets_2076_7256",  # noqa
            "queries.tests.Queries1Tests.test_tickets_2080_3592",  # noqa
            "queries.tests.Queries1Tests.test_tickets_2874_3002",  # noqa
            "queries.tests.Queries1Tests.test_tickets_4088_4306",  # noqa
            "queries.tests.Queries1Tests.test_tickets_5321_7070",  # noqa
            "queries.tests.Queries1Tests.test_tickets_5324_6704",  # noqa
            "queries.tests.Queries1Tests.test_tickets_6180_6203",  # noqa
            "queries.tests.Queries1Tests.test_tickets_7087_12242",  # noqa
            "queries.tests.Queries1Tests.test_tickets_7204_7506",  # noqa
            "queries.tests.Queries1Tests.test_tickets_7448_7707",  # noqa
            "queries.tests.Queries2Tests.test_ticket12239",  # noqa
            "queries.tests.Queries2Tests.test_ticket4289",  # noqa
            "queries.tests.Queries2Tests.test_ticket7759",  # noqa
            "queries.tests.Queries4Tests.test_combine_join_reuse",  # noqa
            "queries.tests.Queries4Tests.test_combine_or_filter_reuse",  # noqa
            "queries.tests.Queries4Tests.test_filter_reverse_non_integer_pk",  # noqa
            "queries.tests.Queries4Tests.test_join_reuse_order",  # noqa
            "queries.tests.Queries4Tests.test_order_by_resetting",  # noqa
            "queries.tests.Queries4Tests.test_order_by_reverse_fk",  # noqa
            "queries.tests.Queries4Tests.test_ticket10181",  # noqa
            "queries.tests.Queries4Tests.test_ticket11811",  # noqa
            "queries.tests.Queries4Tests.test_ticket14876",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_exclude_false",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_filter_false",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_filter_true",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_one2one_exclude_false",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_one2one_exclude_true",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_one2one_filter_false",  # noqa
            "queries.tests.Queries4Tests.test_ticket15316_one2one_filter_true",  # noqa
            "queries.tests.Queries4Tests.test_ticket24525",  # noqa
            "queries.tests.Queries4Tests.test_ticket7095",  # noqa
            "queries.tests.Queries5Tests.test_extra_select_literal_percent_s",  # noqa
            "queries.tests.Queries5Tests.test_ordering",  # noqa
            "queries.tests.Queries5Tests.test_ticket5261",  # noqa
            "queries.tests.Queries5Tests.test_ticket7045",  # noqa
            "queries.tests.Queries5Tests.test_ticket9848",  # noqa
            "queries.tests.Queries6Tests.test_distinct_ordered_sliced_subquery_aggregation",  # noqa
            "queries.tests.Queries6Tests.test_multiple_columns_with_the_same_name_slice",  # noqa
            "queries.tests.Queries6Tests.test_nested_queries_sql",  # noqa
            "queries.tests.Queries6Tests.test_parallel_iterators",  # noqa
            "queries.tests.Queries6Tests.test_ticket3739",  # noqa
            "queries.tests.Queries6Tests.test_ticket_11320",  # noqa
            "queries.tests.Queries6Tests.test_tickets_8921_9188",  # noqa
            "queries.tests.RawQueriesTests.test_ticket14729",  # noqa
            "queries.tests.RelabelCloneTest.test_ticket_19964",  # noqa
            "queries.tests.RelatedLookupTypeTests.test_correct_lookup",  # noqa
            "queries.tests.RelatedLookupTypeTests.test_wrong_backward_lookup",  # noqa
            "queries.tests.RelatedLookupTypeTests.test_wrong_type_lookup",  # noqa
            "queries.tests.ReverseJoinTrimmingTest.test_reverse_trimming",  # noqa
            "queries.tests.SubclassFKTests.test_ticket7778",  # noqa
            "queries.tests.Ticket20101Tests.test_ticket_20101",  # noqa
            "queries.tests.Ticket22429Tests.test_ticket_22429",  # noqa
            "queries.tests.ToFieldTests.test_nested_in_subquery",  # noqa
            "queries.tests.ToFieldTests.test_recursive_fk",  # noqa
            "queries.tests.ToFieldTests.test_recursive_fk_reverse",  # noqa
            "queries.tests.ValuesJoinPromotionTests.test_ticket_21376",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_multiple_select_params_values_order_by",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_select_params_values_order_in_extra",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_values",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_values_list",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_values_order_in_extra",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_values_order_multiple",  # noqa
            "queries.tests.ValuesQuerysetTests.test_extra_values_order_twice",  # noqa
            "queries.tests.ValuesQuerysetTests.test_field_error_values_list",  # noqa
            "queries.tests.ValuesQuerysetTests.test_flat_extra_values_list",  # noqa
            "queries.tests.ValuesQuerysetTests.test_flat_values_list",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_bad_field_name",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_expression",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_expression_with_default_alias",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_flat",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_with_fields",  # noqa
            "queries.tests.ValuesQuerysetTests.test_named_values_list_without_fields",  # noqa
            "queries.tests.WeirdQuerysetSlicingTests.test_empty_resultset_sql",  # noqa
            "queries.tests.WeirdQuerysetSlicingTests.test_empty_sliced_subquery",  # noqa
            "queries.tests.WeirdQuerysetSlicingTests.test_empty_sliced_subquery_exclude",  # noqa
            "queries.tests.WeirdQuerysetSlicingTests.test_tickets_7698_10202",  # noqa
            "queries.tests.WeirdQuerysetSlicingTests.test_zero_length_values_slicing",  # noqa
            "schema.tests.SchemaTests.test_add_datefield_and_datetimefield_use_effective_default",  # noqa
            "schema.tests.SchemaTests.test_add_field",  # noqa
            "schema.tests.SchemaTests.test_add_field_binary",  # noqa
            "schema.tests.SchemaTests.test_add_field_default_dropped",  # noqa
            "schema.tests.SchemaTests.test_add_field_default_transform",  # noqa
            "schema.tests.SchemaTests.test_add_field_remove_field",  # noqa
            "schema.tests.SchemaTests.test_add_field_temp_default",  # noqa
            "schema.tests.SchemaTests.test_add_field_temp_default_boolean",  # noqa
            "schema.tests.SchemaTests.test_add_field_use_effective_default",  # noqa
            "schema.tests.SchemaTests.test_add_foreign_key_long_names",  # noqa
            "schema.tests.SchemaTests.test_add_foreign_key_quoted_db_table",  # noqa
            "schema.tests.SchemaTests.test_add_foreign_object",  # noqa
            "schema.tests.SchemaTests.test_add_remove_index",  # noqa
            "schema.tests.SchemaTests.test_add_textfield_unhashable_default",  # noqa
            "schema.tests.SchemaTests.test_alter",  # noqa
            "schema.tests.SchemaTests.test_alter_auto_field_to_integer_field",  # noqa
            "schema.tests.SchemaTests.test_alter_charfield_to_null",  # noqa
            "schema.tests.SchemaTests.test_alter_field_add_index_to_integerfield",  # noqa
            "schema.tests.SchemaTests.test_alter_field_default_doesnt_perform_queries",  # noqa
            "schema.tests.SchemaTests.test_alter_field_default_dropped",  # noqa
            "schema.tests.SchemaTests.test_alter_field_fk_keeps_index",  # noqa
            "schema.tests.SchemaTests.test_alter_field_fk_to_o2o",  # noqa
            "schema.tests.SchemaTests.test_alter_field_o2o_keeps_unique",  # noqa
            "schema.tests.SchemaTests.test_alter_field_o2o_to_fk",  # noqa
            "schema.tests.SchemaTests.test_alter_fk",  # noqa
            "schema.tests.SchemaTests.test_alter_fk_checks_deferred_constraints",  # noqa
            "schema.tests.SchemaTests.test_alter_fk_to_o2o",  # noqa
            "schema.tests.SchemaTests.test_alter_implicit_id_to_explicit",  # noqa
            "schema.tests.SchemaTests.test_alter_int_pk_to_autofield_pk",  # noqa
            "schema.tests.SchemaTests.test_alter_int_pk_to_bigautofield_pk",  # noqa
            "schema.tests.SchemaTests.test_alter_null_to_not_null",  # noqa
            "schema.tests.SchemaTests.test_alter_null_to_not_null_keeping_default",  # noqa
            "schema.tests.SchemaTests.test_alter_numeric_field_keep_null_status",  # noqa
            "schema.tests.SchemaTests.test_alter_o2o_to_fk",  # noqa
            "schema.tests.SchemaTests.test_alter_text_field",  # noqa
            "schema.tests.SchemaTests.test_alter_textfield_to_null",  # noqa
            "schema.tests.SchemaTests.test_alter_textual_field_keep_null_status",  # noqa
            "schema.tests.SchemaTests.test_alter_to_fk",  # noqa
            "schema.tests.SchemaTests.test_char_field_with_db_index_to_fk",  # noqa
            "schema.tests.SchemaTests.test_check_constraints",  # noqa
            "schema.tests.SchemaTests.test_context_manager_exit",  # noqa
            "schema.tests.SchemaTests.test_create_index_together",  # noqa
            "schema.tests.SchemaTests.test_creation_deletion",  # noqa
            "schema.tests.SchemaTests.test_creation_deletion_reserved_names",  # noqa
            "schema.tests.SchemaTests.test_fk",  # noqa
            "schema.tests.SchemaTests.test_fk_db_constraint",  # noqa
            "schema.tests.SchemaTests.test_fk_to_proxy",  # noqa
            "schema.tests.SchemaTests.test_foreign_key_index_long_names_regression",  # noqa
            "schema.tests.SchemaTests.test_index_together",  # noqa
            "schema.tests.SchemaTests.test_index_together_with_fk",  # noqa
            "schema.tests.SchemaTests.test_indexes",  # noqa
            "schema.tests.SchemaTests.test_m2m",  # noqa
            "schema.tests.SchemaTests.test_m2m_create",  # noqa
            "schema.tests.SchemaTests.test_m2m_create_custom",  # noqa
            "schema.tests.SchemaTests.test_m2m_create_inherited",  # noqa
            "schema.tests.SchemaTests.test_m2m_create_through",  # noqa
            "schema.tests.SchemaTests.test_m2m_create_through_custom",  # noqa
            "schema.tests.SchemaTests.test_m2m_create_through_inherited",  # noqa
            "schema.tests.SchemaTests.test_m2m_custom",  # noqa
            "schema.tests.SchemaTests.test_m2m_db_constraint",  # noqa
            "schema.tests.SchemaTests.test_m2m_db_constraint_custom",  # noqa
            "schema.tests.SchemaTests.test_m2m_db_constraint_inherited",  # noqa
            "schema.tests.SchemaTests.test_m2m_inherited",  # noqa
            "schema.tests.SchemaTests.test_m2m_through_alter",  # noqa
            "schema.tests.SchemaTests.test_m2m_through_alter_custom",  # noqa
            "schema.tests.SchemaTests.test_m2m_through_alter_inherited",  # noqa
            "schema.tests.SchemaTests.test_namespaced_db_table_create_index_name",  # noqa
            "schema.tests.SchemaTests.test_no_db_constraint_added_during_primary_key_change",  # noqa
            "schema.tests.SchemaTests.test_order_index",  # noqa
            "schema.tests.SchemaTests.test_remove_constraints_capital_letters",  # noqa
            "schema.tests.SchemaTests.test_remove_db_index_doesnt_remove_custom_indexes",  # noqa
            "schema.tests.SchemaTests.test_remove_field_check_does_not_remove_meta_constraints",  # noqa
            "schema.tests.SchemaTests.test_remove_field_unique_does_not_remove_meta_constraints",  # noqa
            "schema.tests.SchemaTests.test_remove_index_together_does_not_remove_meta_indexes",  # noqa
            "schema.tests.SchemaTests.test_remove_unique_together_does_not_remove_meta_constraints",  # noqa
            "schema.tests.SchemaTests.test_text_field_with_db_index",  # noqa
            "schema.tests.SchemaTests.test_text_field_with_db_index_to_fk",  # noqa
            "schema.tests.SchemaTests.test_unique",  # noqa
            "schema.tests.SchemaTests.test_unique_and_reverse_m2m",  # noqa
            "schema.tests.SchemaTests.test_unique_no_unnecessary_fk_drops",  # noqa
            "schema.tests.SchemaTests.test_unique_together",  # noqa
            "schema.tests.SchemaTests.test_unique_together_with_fk",  # noqa
            "schema.tests.SchemaTests.test_unique_together_with_fk_with_existing_index",  # noqa
            "schema.tests.SchemaTests.test_unsupported_transactional_ddl_disallowed",  # noqa
            "select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_nullable_relation",  # noqa
            "select_related_onetoone.tests.ReverseSelectRelatedTestCase.test_self_relation",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_actual_expiry",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_clearsessions_command",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_cycle",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_cycle_with_no_session_cache",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_delete",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_extra_session_field",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_flush",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_invalid_key",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_save",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_save_doesnt_clear_data",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_session_get_decoded",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_session_save_does_not_resurrect_session_logged_out_in_other_context",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_session_str",  # noqa
            "sessions_tests.tests.CustomDatabaseSessionTests.test_sessionmanager_save",  # noqa
            "sessions_tests.tests.SessionMiddlewareTests.test_empty_session_saved",  # noqa
            "sitemaps_tests.test_generic.GenericViewsSitemapTests.test_generic_sitemap",  # noqa
            "sitemaps_tests.test_generic.GenericViewsSitemapTests.test_generic_sitemap_attributes",  # noqa
            "sitemaps_tests.test_generic.GenericViewsSitemapTests.test_generic_sitemap_lastmod",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_alternate_i18n_sitemap_index",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_alternate_i18n_sitemap_limited",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_alternate_i18n_sitemap_xdefault",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_cached_sitemap_index",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_empty_page",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_empty_sitemap",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_localized_priority",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_no_section",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_page_not_int",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_paged_sitemap",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_requestsite_sitemap",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_simple_custom_sitemap",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_simple_i18n_sitemap_index",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_simple_sitemap",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_simple_sitemap_index",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_simple_sitemap_section",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_get_urls_no_site_1",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_get_urls_no_site_2",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_item",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_last_modified",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_last_modified_date",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_last_modified_missing",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_last_modified_mixed",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_last_modified_tz",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_not_callable",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemap_without_entries",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemaps_lastmod_ascending",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemaps_lastmod_descending",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemaps_lastmod_mixed_ascending_last_modified_missing",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_sitemaps_lastmod_mixed_descending_last_modified_missing",  # noqa
            "sitemaps_tests.test_http.HTTPSitemapTests.test_x_robots_sitemap",  # noqa
            "sitemaps_tests.test_https.HTTPSDetectionSitemapTests.test_sitemap_index_with_https_request",  # noqa
            "sitemaps_tests.test_https.HTTPSDetectionSitemapTests.test_sitemap_section_with_https_request",  # noqa
            "sitemaps_tests.test_https.HTTPSSitemapTests.test_secure_sitemap_index",  # noqa
            "sitemaps_tests.test_https.HTTPSSitemapTests.test_secure_sitemap_section",  # noqa
            "sitemaps_tests.test_management.PingGoogleTests.test_args",  # noqa
            "sitemaps_tests.test_management.PingGoogleTests.test_default",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_exact_url",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_global",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_index",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_insecure",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_no_sites",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_get_sitemap_full_url_not_detected",  # noqa
            "sitemaps_tests.test_utils.PingGoogleTests.test_something",  # noqa
            "string_lookup.tests.StringLookupTests.test_queries_on_textfields",  # noqa
            "test_client.tests.ClientTest.test_empty_post",  # noqa
            "test_client.tests.ClientTest.test_exc_info",  # noqa
            "test_client.tests.ClientTest.test_exc_info_none",  # noqa
            "test_client.tests.ClientTest.test_exception_following_nested_client_request",  # noqa
            "test_client.tests.ClientTest.test_external_redirect",  # noqa
            "test_client.tests.ClientTest.test_external_redirect_with_fetch_error_msg",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_get_head_query_string",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_preserves_get_params",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_preserves_post_data",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_preserves_put_body",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_preserves_query_string",  # noqa
            "test_client.tests.ClientTest.test_follow_307_and_308_redirect",  # noqa
            "test_client.tests.ClientTest.test_follow_redirect",  # noqa
            "test_client.tests.ClientTest.test_follow_relative_redirect",  # noqa
            "test_client.tests.ClientTest.test_follow_relative_redirect_no_trailing_slash",  # noqa
            "test_client.tests.ClientTest.test_force_login_with_backend",  # noqa
            "test_client.tests.ClientTest.test_force_login_with_backend_missing_get_user",  # noqa
            "test_client.tests.ClientTest.test_force_login_without_backend",  # noqa
            "test_client.tests.ClientTest.test_form_error",  # noqa
            "test_client.tests.ClientTest.test_form_error_with_template",  # noqa
            "test_client.tests.ClientTest.test_get_data_none",  # noqa
            "test_client.tests.ClientTest.test_get_post_view",  # noqa
            "test_client.tests.ClientTest.test_get_view",  # noqa
            "test_client.tests.ClientTest.test_incomplete_data_form",  # noqa
            "test_client.tests.ClientTest.test_incomplete_data_form_with_template",  # noqa
            "test_client.tests.ClientTest.test_insecure",  # noqa
            "test_client.tests.ClientTest.test_json_encoder_argument",  # noqa
            "test_client.tests.ClientTest.test_json_serialization",  # noqa
            "test_client.tests.ClientTest.test_logout",  # noqa
            "test_client.tests.ClientTest.test_logout_cookie_sessions",  # noqa
            "test_client.tests.ClientTest.test_logout_with_force_login",  # noqa
            "test_client.tests.ClientTest.test_mail_sending",  # noqa
            "test_client.tests.ClientTest.test_mass_mail_sending",  # noqa
            "test_client.tests.ClientTest.test_notfound_response",  # noqa
            "test_client.tests.ClientTest.test_permanent_redirect",  # noqa
            "test_client.tests.ClientTest.test_post",  # noqa
            "test_client.tests.ClientTest.test_post_data_none",  # noqa
            "test_client.tests.ClientTest.test_put",  # noqa
            "test_client.tests.ClientTest.test_query_string_encoding",  # noqa
            "test_client.tests.ClientTest.test_raw_post",  # noqa
            "test_client.tests.ClientTest.test_redirect",  # noqa
            "test_client.tests.ClientTest.test_redirect_http",  # noqa
            "test_client.tests.ClientTest.test_redirect_https",  # noqa
            "test_client.tests.ClientTest.test_redirect_to_strange_location",  # noqa
            "test_client.tests.ClientTest.test_redirect_with_query",  # noqa
            "test_client.tests.ClientTest.test_redirect_with_query_ordering",  # noqa
            "test_client.tests.ClientTest.test_relative_redirect",  # noqa
            "test_client.tests.ClientTest.test_relative_redirect_no_trailing_slash",  # noqa
            "test_client.tests.ClientTest.test_response_attached_request",  # noqa
            "test_client.tests.ClientTest.test_response_headers",  # noqa
            "test_client.tests.ClientTest.test_response_raises_multi_arg_exception",  # noqa
            "test_client.tests.ClientTest.test_response_resolver_match",  # noqa
            "test_client.tests.ClientTest.test_response_resolver_match_redirect_follow",  # noqa
            "test_client.tests.ClientTest.test_response_resolver_match_regular_view",  # noqa
            "test_client.tests.ClientTest.test_reverse_lazy_decodes",  # noqa
            "test_client.tests.ClientTest.test_secure",  # noqa
            "test_client.tests.ClientTest.test_session_engine_is_invalid",  # noqa
            "test_client.tests.ClientTest.test_session_modifying_view",  # noqa
            "test_client.tests.ClientTest.test_sessions_app_is_not_installed",  # noqa
            "test_client.tests.ClientTest.test_temporary_redirect",  # noqa
            "test_client.tests.ClientTest.test_trace",  # noqa
            "test_client.tests.ClientTest.test_unknown_page",  # noqa
            "test_client.tests.ClientTest.test_uploading_named_temp_file",  # noqa
            "test_client.tests.ClientTest.test_uploading_temp_file",  # noqa
            "test_client.tests.ClientTest.test_url_parameters",  # noqa
            "test_client.tests.ClientTest.test_valid_form",  # noqa
            "test_client.tests.ClientTest.test_valid_form_with_hints",  # noqa
            "test_client.tests.ClientTest.test_valid_form_with_template",  # noqa
            "test_client.tests.ClientTest.test_view_with_bad_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_exception",  # noqa
            "test_client.tests.ClientTest.test_view_with_force_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_force_login_and_custom_redirect",  # noqa
            "test_client.tests.ClientTest.test_view_with_inactive_force_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_inactive_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_login_and_custom_redirect",  # noqa
            "test_client.tests.ClientTest.test_view_with_login_when_sessions_app_is_not_installed",  # noqa
            "test_client.tests.ClientTest.test_view_with_method_force_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_method_login",  # noqa
            "test_client.tests.ClientTest.test_view_with_method_permissions",  # noqa
            "test_client.tests.ClientTest.test_view_with_permissions",  # noqa
            "test_client.tests.ClientTest.test_view_with_permissions_exception",  # noqa
            "test_client_regress.tests.AssertTemplateUsedTests.test_multiple_context",  # noqa
            "test_client_regress.tests.AssertTemplateUsedTests.test_no_context",  # noqa
            "test_client_regress.tests.AssertTemplateUsedTests.test_single_context",  # noqa
            "test_client_regress.tests.AssertTemplateUsedTests.test_template_rendered_multiple_times",  # noqa
            "test_client_regress.tests.ContextTests.test_15368",  # noqa
            "test_client_regress.tests.ContextTests.test_contextlist_get",  # noqa
            "test_client_regress.tests.ContextTests.test_contextlist_keys",  # noqa
            "test_client_regress.tests.ContextTests.test_inherited_context",  # noqa
            "test_client_regress.tests.ContextTests.test_nested_requests",  # noqa
            "test_client_regress.tests.ContextTests.test_single_context",  # noqa
            "test_client_regress.tests.ExceptionTests.test_exception_cleared",  # noqa
            "test_client_regress.tests.LoginTests.test_login_different_client",  # noqa
            "test_client_regress.tests.SessionEngineTests.test_login",  # noqa
            "test_client_regress.tests.SessionTests.test_login_with_user",  # noqa
            "test_client_regress.tests.SessionTests.test_login_without_signal",  # noqa
            "test_client_regress.tests.SessionTests.test_logout",  # noqa
            "test_client_regress.tests.SessionTests.test_logout_with_custom_auth_backend",  # noqa
            "test_client_regress.tests.SessionTests.test_logout_with_custom_user",  # noqa
            "test_client_regress.tests.SessionTests.test_logout_with_user",  # noqa
            "test_client_regress.tests.SessionTests.test_logout_without_user",  # noqa
            "test_client_regress.tests.SessionTests.test_session",  # noqa
            "test_client_regress.tests.SessionTests.test_session_initiated",  # noqa
            "timezones.tests.NewDatabaseTests.test_null_datetime",
            "transactions.tests.NonAutocommitTests.test_orm_query_after_error_and_rollback",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_empty_update_fields",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_num_queries_inheritance",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_select_related_only_interaction",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_basic",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_fk_defer",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_incorrect_params",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_inheritance",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_inheritance_defer",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_inheritance_with_proxy_model",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_m2m",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_only_1",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_only_repeated",  # noqa
            "update_only_fields.tests.UpdateOnlyFieldsTests.test_update_fields_signals",  # noqa
            "validation.tests.BaseModelValidationTests.test_correct_FK_value_validates",  # noqa
            "validation.tests.BaseModelValidationTests.test_limited_FK_raises_error",  # noqa
            "validation.tests.GenericIPAddressFieldTests.test_empty_generic_ip_passes",  # noqa
            "validation.tests.GenericIPAddressFieldTests.test_v4_unpack_uniqueness_detection",  # noqa
            "validation.tests.GenericIPAddressFieldTests.test_v6_uniqueness_detection",  # noqa
            )
