import unittest

from pyramid import testing
from pyramid.util import text_


class TestXHRPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import XHRPredicate

        return XHRPredicate(val, None)

    def test___call___true(self):
        inst = self._makeOne(True)
        request = Dummy()
        request.is_xhr = True
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne(True)
        request = Dummy()
        request.is_xhr = False
        result = inst(None, request)
        self.assertFalse(result)

    def test_text(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.text(), 'xhr = True')

    def test_phash(self):
        inst = self._makeOne(True)
        self.assertEqual(inst.phash(), 'xhr = True')


class TestRequestMethodPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import RequestMethodPredicate

        return RequestMethodPredicate(val, None)

    def test_ctor_get_but_no_head(self):
        inst = self._makeOne('GET')
        self.assertEqual(inst.val, ('GET', 'HEAD'))

    def test___call___true_single(self):
        inst = self._makeOne('GET')
        request = Dummy()
        request.method = 'GET'
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_multi(self):
        inst = self._makeOne(('GET', 'HEAD'))
        request = Dummy()
        request.method = 'GET'
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne(('GET', 'HEAD'))
        request = Dummy()
        request.method = 'POST'
        result = inst(None, request)
        self.assertFalse(result)

    def test_text(self):
        inst = self._makeOne(('HEAD', 'GET'))
        self.assertEqual(inst.text(), 'request_method = GET,HEAD')

    def test_phash(self):
        inst = self._makeOne(('HEAD', 'GET'))
        self.assertEqual(inst.phash(), 'request_method = GET,HEAD')


class TestPathInfoPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import PathInfoPredicate

        return PathInfoPredicate(val, None)

    def test_ctor_compilefail(self):
        from pyramid.exceptions import ConfigurationError

        self.assertRaises(ConfigurationError, self._makeOne, '\\')

    def test___call___true(self):
        inst = self._makeOne(r'/\d{2}')
        request = Dummy()
        request.upath_info = text_('/12')
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne(r'/\d{2}')
        request = Dummy()
        request.upath_info = text_('/n12')
        result = inst(None, request)
        self.assertFalse(result)

    def test_text(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.text(), 'path_info = /')

    def test_phash(self):
        inst = self._makeOne('/')
        self.assertEqual(inst.phash(), 'path_info = /')


class TestRequestParamPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import RequestParamPredicate

        return RequestParamPredicate(val, None)

    def test___call___true_exists(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.params = {'abc': 1}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_withval(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.params = {'abc': '1'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_multi(self):
        inst = self._makeOne(('abc', '=def =2= '))
        request = Dummy()
        request.params = {'abc': '1', '=def': '2='}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false_multi(self):
        inst = self._makeOne(('abc=3', 'def =2 '))
        request = Dummy()
        request.params = {'abc': '3', 'def': '1'}
        result = inst(None, request)
        self.assertFalse(result)

    def test___call___false(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.params = {}
        result = inst(None, request)
        self.assertFalse(result)

    def test_text_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.text(), 'request_param abc')

    def test_text_exists_equal_sign(self):
        inst = self._makeOne('=abc')
        self.assertEqual(inst.text(), 'request_param =abc')

    def test_text_withval(self):
        inst = self._makeOne('abc=  1')
        self.assertEqual(inst.text(), 'request_param abc=1')

    def test_text_multi(self):
        inst = self._makeOne(('abc=  1', 'def'))
        self.assertEqual(inst.text(), 'request_param abc=1,def')

    def test_text_multi_equal_sign(self):
        inst = self._makeOne(('abc=  1', '=def= 2'))
        self.assertEqual(inst.text(), 'request_param =def=2,abc=1')

    def test_phash_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.phash(), 'request_param abc')

    def test_phash_exists_equal_sign(self):
        inst = self._makeOne('=abc')
        self.assertEqual(inst.phash(), 'request_param =abc')

    def test_phash_withval(self):
        inst = self._makeOne('abc=   1')
        self.assertEqual(inst.phash(), "request_param abc=1")


class TestMatchParamPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import MatchParamPredicate

        return MatchParamPredicate(val, None)

    def test___call___true_single(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.matchdict = {'abc': '1'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_multi(self):
        inst = self._makeOne(('abc=1', 'def=2'))
        request = Dummy()
        request.matchdict = {'abc': '1', 'def': '2'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.matchdict = {}
        result = inst(None, request)
        self.assertFalse(result)

    def test___call___matchdict_is_None(self):
        inst = self._makeOne('abc=1')
        request = Dummy()
        request.matchdict = None
        result = inst(None, request)
        self.assertFalse(result)

    def test_text(self):
        inst = self._makeOne(('def=  1', 'abc =2'))
        self.assertEqual(inst.text(), 'match_param abc=2,def=1')

    def test_phash(self):
        inst = self._makeOne(('def=  1', 'abc =2'))
        self.assertEqual(inst.phash(), 'match_param abc=2,def=1')


class TestCustomPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import CustomPredicate

        return CustomPredicate(val, None)

    def test___call___true(self):
        def func(context, request):
            self.assertEqual(context, None)
            self.assertEqual(request, None)
            return True

        inst = self._makeOne(func)
        result = inst(None, None)
        self.assertTrue(result)

    def test___call___false(self):
        def func(context, request):
            self.assertEqual(context, None)
            self.assertEqual(request, None)
            return False

        inst = self._makeOne(func)
        result = inst(None, None)
        self.assertFalse(result)

    def test_text_func_has___text__(self):
        pred = predicate()
        pred.__text__ = 'text'
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), 'text')

    def test_text_func_repr(self):
        pred = predicate()
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), 'custom predicate: object predicate')

    def test_phash(self):
        pred = predicate()
        inst = self._makeOne(pred)
        self.assertEqual(inst.phash(), 'custom:1')


class TestTraversePredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import TraversePredicate

        return TraversePredicate(val, None)

    def test___call__traverse_has_remainder_already(self):
        inst = self._makeOne('/1/:a/:b')
        info = {'traverse': 'abc'}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(info, {'traverse': 'abc'})

    def test___call__traverse_matches(self):
        inst = self._makeOne('/1/:a/:b')
        info = {'match': {'a': 'a', 'b': 'b'}}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(
            info, {'match': {'a': 'a', 'b': 'b', 'traverse': ('1', 'a', 'b')}}
        )

    def test___call__traverse_matches_with_highorder_chars(self):
        inst = self._makeOne(text_(b'/La Pe\xc3\xb1a/{x}', 'utf-8'))
        info = {'match': {'x': text_(b'Qu\xc3\xa9bec', 'utf-8')}}
        request = Dummy()
        result = inst(info, request)
        self.assertEqual(result, True)
        self.assertEqual(
            info['match']['traverse'],
            (
                text_(b'La Pe\xc3\xb1a', 'utf-8'),
                text_(b'Qu\xc3\xa9bec', 'utf-8'),
            ),
        )

    def test_text(self):
        inst = self._makeOne('/abc')
        self.assertEqual(inst.text(), 'traverse matchdict pseudo-predicate')

    def test_phash(self):
        inst = self._makeOne('/abc')
        self.assertEqual(inst.phash(), '')


class TestHeaderPredicate(unittest.TestCase):
    def _makeOne(self, val):
        from pyramid.predicates import HeaderPredicate

        return HeaderPredicate(val, None)

    def test___call___true_exists(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.headers = {'abc': 1}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_withval(self):
        inst = self._makeOne('abc:1')
        request = Dummy()
        request.headers = {'abc': '1'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___true_withregex(self):
        inst = self._makeOne(r'abc:\d+')
        request = Dummy()
        request.headers = {'abc': '1'}
        result = inst(None, request)
        self.assertTrue(result)

    def test___call___false_withregex(self):
        inst = self._makeOne(r'abc:\d+')
        request = Dummy()
        request.headers = {'abc': 'a'}
        result = inst(None, request)
        self.assertFalse(result)

    def test___call___false(self):
        inst = self._makeOne('abc')
        request = Dummy()
        request.headers = {}
        result = inst(None, request)
        self.assertFalse(result)

    def test_text_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.text(), 'header abc')

    def test_text_withval(self):
        inst = self._makeOne('abc:1')
        self.assertEqual(inst.text(), 'header abc=1')

    def test_text_withregex(self):
        inst = self._makeOne(r'abc:\d+')
        self.assertEqual(inst.text(), r'header abc=\d+')

    def test_phash_exists(self):
        inst = self._makeOne('abc')
        self.assertEqual(inst.phash(), 'header abc')

    def test_phash_withval(self):
        inst = self._makeOne('abc:1')
        self.assertEqual(inst.phash(), "header abc=1")

    def test_phash_withregex(self):
        inst = self._makeOne(r'abc:\d+')
        self.assertEqual(inst.phash(), r'header abc=\d+')


class Test_PhysicalPathPredicate(unittest.TestCase):
    def _makeOne(self, val, config):
        from pyramid.predicates import PhysicalPathPredicate

        return PhysicalPathPredicate(val, config)

    def test_text(self):
        inst = self._makeOne('/', None)
        self.assertEqual(inst.text(), "physical_path = ('',)")

    def test_phash(self):
        inst = self._makeOne('/', None)
        self.assertEqual(inst.phash(), "physical_path = ('',)")

    def test_it_call_val_tuple_True(self):
        inst = self._makeOne(('', 'abc'), None)
        root = Dummy()
        root.__name__ = ''
        root.__parent__ = None
        context = Dummy()
        context.__name__ = 'abc'
        context.__parent__ = root
        self.assertTrue(inst(context, None))

    def test_it_call_val_list_True(self):
        inst = self._makeOne(['', 'abc'], None)
        root = Dummy()
        root.__name__ = ''
        root.__parent__ = None
        context = Dummy()
        context.__name__ = 'abc'
        context.__parent__ = root
        self.assertTrue(inst(context, None))

    def test_it_call_val_str_True(self):
        inst = self._makeOne('/abc', None)
        root = Dummy()
        root.__name__ = ''
        root.__parent__ = None
        context = Dummy()
        context.__name__ = 'abc'
        context.__parent__ = root
        self.assertTrue(inst(context, None))

    def test_it_call_False(self):
        inst = self._makeOne('/', None)
        root = Dummy()
        root.__name__ = ''
        root.__parent__ = None
        context = Dummy()
        context.__name__ = 'abc'
        context.__parent__ = root
        self.assertFalse(inst(context, None))

    def test_it_call_context_has_no_name(self):
        inst = self._makeOne('/', None)
        context = Dummy()
        self.assertFalse(inst(context, None))


class Test_EffectivePrincipalsPredicate(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def _makeOne(self, val, config):
        from pyramid.predicates import EffectivePrincipalsPredicate

        return EffectivePrincipalsPredicate(val, config)

    def _testing_authn_policy(self, userid, groupids=tuple()):
        from pyramid.interfaces import IAuthenticationPolicy, ISecurityPolicy
        from pyramid.authorization import Everyone, Authenticated
        from pyramid.security import LegacySecurityPolicy

        class DummyPolicy:
            def effective_principals(self, request):
                p = [Everyone]
                if userid:
                    p.append(Authenticated)
                    p.append(userid)
                    p.extend(groupids)
                return p

        registry = self.config.registry
        registry.registerUtility(DummyPolicy(), IAuthenticationPolicy)
        registry.registerUtility(LegacySecurityPolicy(), ISecurityPolicy)

    def test_text(self):
        inst = self._makeOne(('verna', 'fred'), None)
        self.assertEqual(
            inst.text(), "effective_principals = ['fred', 'verna']"
        )

    def test_text_noniter(self):
        inst = self._makeOne('verna', None)
        self.assertEqual(inst.text(), "effective_principals = ['verna']")

    def test_phash(self):
        inst = self._makeOne(('verna', 'fred'), None)
        self.assertEqual(
            inst.phash(), "effective_principals = ['fred', 'verna']"
        )

    def test_it_call_no_authentication_policy(self):
        request = testing.DummyRequest()
        inst = self._makeOne(('verna', 'fred'), None)
        context = Dummy()
        self.assertFalse(inst(context, request))

    def test_it_call_authentication_policy_provides_superset(self):
        request = testing.DummyRequest()
        self._testing_authn_policy('fred', groupids=('verna', 'bambi'))
        inst = self._makeOne(('verna', 'fred'), None)
        context = Dummy()
        self.assertTrue(inst(context, request))

    def test_it_call_authentication_policy_provides_superset_implicit(self):
        from pyramid.authorization import Authenticated

        request = testing.DummyRequest()
        self._testing_authn_policy('fred', groupids=('verna', 'bambi'))
        inst = self._makeOne(Authenticated, None)
        context = Dummy()
        self.assertTrue(inst(context, request))

    def test_it_call_authentication_policy_doesnt_provide_superset(self):
        request = testing.DummyRequest()
        self._testing_authn_policy('fred')
        inst = self._makeOne(('verna', 'fred'), None)
        context = Dummy()
        self.assertFalse(inst(context, request))


class TestNotted(unittest.TestCase):
    def _makeOne(self, predicate):
        from pyramid.predicates import Notted

        return Notted(predicate)

    def test_it_with_phash_val(self):
        pred = DummyPredicate('val')
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), '!val')
        self.assertEqual(inst.phash(), '!val')
        self.assertEqual(inst(None, None), False)

    def test_it_without_phash_val(self):
        pred = DummyPredicate('')
        inst = self._makeOne(pred)
        self.assertEqual(inst.text(), '')
        self.assertEqual(inst.phash(), '')
        self.assertEqual(inst(None, None), True)


class predicate(object):
    def __repr__(self):
        return 'predicate'

    def __hash__(self):
        return 1


class Dummy(object):
    pass


class DummyPredicate(object):
    def __init__(self, result):
        self.result = result

    def text(self):
        return self.result

    phash = text

    def __call__(self, context, request):
        return True
