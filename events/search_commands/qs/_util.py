# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

import logging
import ast

from django.db.models import F, Value, Q, Func
from django.db.models.fields.json import KT
from django.db.models import CharField, TextField, IntegerField, FloatField, BooleanField, DateField, DateTimeField, TimeField, DecimalField
from django.db.models import Sum, Avg, Count, Max, Min, StdDev, Variance
from django.db.models.functions import (
    Lower,
    Upper,
    Length,
    Trim,
    Cast,
    Coalesce,
    Concat,
    Greatest,
    JSONObject,
    Least,
    LPad,
    RPad,
    LTrim,
    RTrim,
    Substr,
    Replace,
    Reverse,
    Now,
    TruncDate,
    TruncMonth,
    TruncYear,
    StrIndex,
    Abs,
    # Acos,
    # Asin,
    # Atan,
    ATan2,
    Ceil,
    Cos,
    Cot,
    Degrees,
    Exp,
    Floor,
    Ln,
    Log,
    # Log10,
    Mod,
    Pi,
    Power,
    Radians,
    Round,
    Sign,
    Sin,
    Sqrt,
    Tan,
    Trunc,
    Extract,
    ExtractDay,
    ExtractHour,
    ExtractMinute,
    ExtractMonth,
    ExtractQuarter,
    ExtractSecond,
    ExtractWeek,
    ExtractWeekDay,
    ExtractYear,
)

from events.util import cast

SUPPORTED_FUNCTIONS = {
    'Lower': Lower,
    'Upper': Upper,
    'Length': Length,
    'Trim': Trim,
    'Cast': Cast,
    'Coalesce': Coalesce,
    'Concat': Concat,
    'Greatest': Greatest,
    'JSONObject': JSONObject,
    'Least': Least,
    'LPad': LPad,
    'RPad': RPad,
    'LTrim': LTrim,
    'RTrim': RTrim,
    'Substr': Substr,
    'Replace': Replace,
    'Reverse': Reverse,
    'Value': Value,
    'F': F,
    'Q': Q,
    'Func': Func,
    'Now': Now,
    'TruncDate': TruncDate,
    'TruncMonth': TruncMonth,
    'TruncYear': TruncYear,
    'StrIndex': StrIndex,
    'Abs': Abs,
    # 'Acos': Acos,
    # 'Asin': Asin,
    # 'Atan': Atan,
    'ATan2': ATan2,
    'Ceil': Ceil,
    'Cos': Cos,
    'Cot': Cot,
    'Degrees': Degrees,
    'Exp': Exp,
    'Floor': Floor,
    'KT': KT,
    'Ln': Ln,
    'Log': Log,
    # 'Log10': Log10,
    'Mod': Mod,
    'Pi': Pi,
    'Power': Power,
    'Radians': Radians,
    'Round': Round,
    'Sign': Sign,
    'Sin': Sin,
    'Sqrt': Sqrt,
    'Tan': Tan,
    'Trunc': Trunc,
    'Extract': Extract,
    'ExtractDay': ExtractDay,
    'ExtractHour': ExtractHour,
    'ExtractMinute': ExtractMinute,
    'ExtractMonth': ExtractMonth,
    'ExtractQuarter': ExtractQuarter,
    'ExtractSecond': ExtractSecond,
    'ExtractWeek': ExtractWeek,
    'ExtractWeekDay': ExtractWeekDay,
    'ExtractYear': ExtractYear,
}

AGGREGATION_FUNCTIONS = {
    'Sum': Sum,
    'Avg': Avg,
    'Count': Count,
    'Max': Max,
    'Min': Min,
    'StdDev': StdDev,
    'Variance': Variance,
}

FIELD_CLASSES = {
    'CharField': CharField,
    'TextField': TextField,
    'IntegerField': IntegerField,
    'FloatField': FloatField,
    'BooleanField': BooleanField,
    'DateField': DateField,
    'DateTimeField': DateTimeField,
    'TimeField': TimeField,
    'DecimalField': DecimalField,
}

def evaluate_node(node):
    """
    Evaluate an AST node and return its corresponding value.

    Args:
        node: The AST node to evaluate.

    Returns:
        The evaluated value of the node.
    """
    if isinstance(node, list):
        logging.debug(f"Evaluating list of nodes: {[repr(n) for n in node]}")
        return [evaluate_node(n) for n in node]
    logging.debug(f"Evaluating node: {repr(node)}")
    if isinstance(node, ast.Call):
        func_name = node.func.id
        args = [evaluate_node(arg) for arg in node.args]
        kwargs = {kw.arg: evaluate_node(kw.value) for kw in node.keywords}
        logging.debug(f"Function call: {func_name} with args: {args} and kwargs: {kwargs}")
        return func_name, args, kwargs
    elif isinstance(node, ast.Assign):
        target = node.targets[0].id
        value = evaluate_node(node.value)
        return {target: value}
    elif isinstance(node, ast.Expr):
        return evaluate_node(node.value)
    elif isinstance(node, ast.Constant):
        logging.debug(f"Constant value: {node.value}")
        return node.value
    elif isinstance(node, ast.Name):
        logging.debug(f"Name identifier: {node.id}")
        return node.id
    elif isinstance(node, ast.Attribute):
        attr = f"{evaluate_node(node.value)}__{node.attr}"
        logging.debug(f"Attribute: {attr}")
        return attr
    elif isinstance(node, ast.BinOp):
        left = evaluate_node(node.left)
        right = evaluate_node(node.right)
        op = node.op
        return ('BinOp', left, op, right)
    elif isinstance(node, ast.UnaryOp):
        operand = evaluate_node(node.operand)
        op = node.op
        return ('UnaryOp', operand, op)
    else:
        raise ValueError(f"Unsupported AST node type: {type(node)}")

def parse_field_expressions(field_expressions):
    """
    Parse a list of field expressions into AST nodes.

    Args:
        field_expressions: List of field expressions as strings.

    Returns:
        List of parsed expressions.
    """
    parsed_expressions = []
    for expr in field_expressions:
        logging.debug(f"Parsing field expression: {expr}")
        try:
            tree = ast.parse(expr, mode='single')
            parsed_expressions.extend(evaluate_node(tree.body))
        except SyntaxError as e:
            logging.error(f"Syntax error in expression '{expr}': {e}")
            raise
    return parsed_expressions

def parse_function_args(func_name, func_args):
    """
    Parse function arguments into positional and keyword arguments.

    Args:
        func_name: The name of the function.
        func_args: List of function arguments as strings.

    Returns:
        Tuple of positional arguments and keyword arguments.
    """
    args = []
    kwargs = {}
    for arg in func_args:
        if '=' in arg:
            key, value = arg.split('=', 1)
            key = key.strip()
            value = value.strip()
            kwargs[key] = value
        else:
            args.append(arg.strip())
    return args, kwargs

def generate_keyword_args(parsed_expressions):
    """
    Generate positional and keyword arguments from parsed expressions.

    Args:
        parsed_expressions: List of parsed expressions.

    Returns:
        Tuple of positional arguments and keyword arguments.
    """
    log = logging.getLogger(__name__)
    keyword_args = {}
    positional_args = []

    def convert_to_django_expression(expr):
        log.debug(f"Converting to Django expression: {expr}")
        if isinstance(expr, tuple) and expr[0] == 'BinOp':
            _, left, op, right = expr
            left_expr = convert_to_django_expression(left)
            right_expr = convert_to_django_expression(right)
            if isinstance(op, ast.Add):
                return left_expr + right_expr
            elif isinstance(op, ast.Sub):
                return left_expr - right_expr
            elif isinstance(op, ast.Mult):
                return left_expr * right_expr
            elif isinstance(op, ast.Div):
                return left_expr / right_expr
            elif isinstance(op, ast.Mod):
                return left_expr % right_expr
            elif isinstance(op, ast.Pow):
                return left_expr ** right_expr
            elif isinstance(op, ast.BitOr):
                return left_expr | right_expr
            elif isinstance(op, ast.BitAnd):
                return left_expr & right_expr
            elif isinstance(op, ast.BitXor):
                return left_expr & right_expr
            else:
                raise ValueError(f"Unsupported binary operator: {type(op)}")
        elif isinstance(expr, tuple) and expr[0] == 'UnaryOp':
            _, operand, op = expr
            operand_expr = convert_to_django_expression(operand)
            if isinstance(op, ast.USub):
                return -operand_expr
            elif isinstance(op, ast.Invert):
                return ~operand_expr
            else:
                raise ValueError(f"Unsupported unary operator: {type(op)}")
        elif isinstance(expr, tuple):
            func_name, args, kwargs = expr
            log.debug(f"Function name: {func_name}, args: {args}, kwargs: {kwargs}")
            args = [convert_to_django_expression(arg) for arg in args]
            kwargs = {key: convert_to_django_expression(value) for key, value in kwargs.items()}
            func_class = SUPPORTED_FUNCTIONS.get(func_name)
            if func_class:
                log.debug(f"Using Django function: {func_name}")
                return func_class(*args, **kwargs)
            elif func_name in AGGREGATION_FUNCTIONS:
                func_class = AGGREGATION_FUNCTIONS[func_name]
                log.debug(f"Using aggregation function: {func_name}")
                return func_class(*args, **kwargs)
            else:
                log.error(f"Function {func_name} is not supported")
                raise ValueError(f"Function {func_name} is not supported")
        elif isinstance(expr, str):
            log.debug(f"Processing string expression: {expr}")
            # if expr.startswith('F(') and expr.endswith(')'):
            #     log.debug(f"Detected F expression: {expr}")
            #     return F(expr[2:-1].strip())
            # elif expr.startswith('Value(') and expr.endswith(')'):
            #     log.debug(f"Detected Value expression: {expr}")
            #     return Value(cast(expr[6:-1].strip()))
            if expr in FIELD_CLASSES:
                log.debug(f"Detected field class: {expr}")
                return FIELD_CLASSES[expr]()
            else:
                log.debug(f"Casting expression: {expr}")
                return cast(expr.strip())
        elif isinstance(expr, dict):
            log.debug(f"Processing dictionary expression: {expr}")
            return {key: convert_to_django_expression(value) for key, value in expr.items()}
        else:
            log.debug(f"Returning expression as is: {expr}")
            return expr

    for expr in parsed_expressions:
        if isinstance(expr, dict):
            keyword_args.update(convert_to_django_expression(expr))
        else:
            positional_args.append(convert_to_django_expression(expr))

    log.debug(f"Generated positional_args: {positional_args}, keyword_args: {keyword_args}")
    return positional_args, keyword_args
