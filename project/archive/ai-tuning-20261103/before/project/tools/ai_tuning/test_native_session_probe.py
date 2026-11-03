"""CLI and actual forwarding-expression checks; no native I/O or files created."""
import argparse
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import native_session_probe as probe


class UserRootArgumentTests(unittest.TestCase):
    def arguments(self):
        values=[]
        for name in ('output','binary','source','native-directory','installed','rh-package','reader','reference'):
            values.extend(('--'+name, 'fixture-'+name))
        return values+['--sha256','fixture-sha','--turn','110']

    def test_user_root_flag_is_optional(self):
        args=probe.parser().parse_args(self.arguments())
        self.assertIsNone(args.user_root)

    def test_user_root_flag_preserves_path(self):
        value=Path('fixture-native-user')
        args=probe.parser().parse_args(self.arguments()+['--user-root',str(value)])
        self.assertEqual(args.user_root,value)
        self.assertIsInstance(args.user_root,Path)

    def test_actual_factory_call_forwards_explicit_and_legacy_namespace_values(self):
        # Evaluate only the real factory call node. Running the surrounding
        # session would launch native work, which this focused check excludes.
        tree=ast.parse(Path(probe.__file__).read_text(encoding='utf-8'))
        run=next(node for node in tree.body if isinstance(node,ast.FunctionDef)and node.name=='run')
        call=next(node for node in ast.walk(run)if isinstance(node,ast.Call)
                  and isinstance(node.func,ast.Name)and node.func.id=='make_probe_controller')
        expression=compile(ast.Expression(body=call),str(probe.__file__),'eval')
        value=Path('fixture-native-user')
        for args,expected in ((argparse.Namespace(user_root=value),value),
                              (argparse.Namespace(user_root=None),None),(SimpleNamespace(),None)):
            with self.subTest(args=args):
                factory=Mock();out=Path('fixture-output')
                result=eval(expression,{'make_probe_controller':factory,'out':out,'a':args})
                factory.assert_called_once_with(out,user_root=expected)
                self.assertIs(result,factory.return_value)


if __name__=='__main__':unittest.main()
