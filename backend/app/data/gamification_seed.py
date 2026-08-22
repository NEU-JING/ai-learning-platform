"""Gamification seed data — badges 定义 + 每日挑战题库 (Phase 4).

幂等：已存在则不重复插入（create_only 语义）。
每日挑战按日期唯一；seed 今天起连续 CHALLENGE_DAYS 天。
"""

import datetime
import logging

from sqlalchemy.orm import Session

from app.models import Badge, DailyChallenge

logger = logging.getLogger(__name__)

CHALLENGE_DAYS = 14

# ── 徽章定义 ────────────────────────────────────────────────────────────────
BADGES = [
    {
        "code": "first_lab",
        "name": "首个实验",
        "description": "完成自己的第一个实验",
        "icon": "🏅",
        "criteria": {"type": "first_lab"},
    },
    {
        "code": "chain_complete",
        "name": "任务链达人",
        "description": "完整打通一条任务链",
        "icon": "🏆",
        "criteria": {"type": "chain_complete"},
    },
    {
        "code": "streak_7",
        "name": "连击7天",
        "description": "连续7天完成每日挑战",
        "icon": "🔥",
        "criteria": {"type": "streak_days", "value": 7},
    },
]

# ── 每日挑战题库（经典 Python 小任务）───────────────────────────────────────
# 每个挑战 = 一个函数任务；test_cases 为 Python 断言脚本（割一行为一测试）
DAILY_CHALLENGES = [
    {
        "task": "写一个函数 is_even(n)，返回 n 是否为偶数。",
        "test_cases": "assert is_even(2) == True\nassert is_even(3) == False\nassert is_even(0) == True",
        "xp_reward": 20,
    },
    {
        "task": "写一个函数 sum_list(nums)，返回列表中所有数字之和（空列表返回 0）。",
        "test_cases": "assert sum_list([1,2,3]) == 6\nassert sum_list([]) == 0\nassert sum_list([-1,1]) == 0",
        "xp_reward": 20,
    },
    {
        "task": "写一个函数 reverse_string(s)，返回字符串反转。",
        "test_cases": "assert reverse_string('abc') == 'cba'\nassert reverse_string('a') == 'a'\nassert reverse_string('') == ''",
        "xp_reward": 20,
    },
    {
        "task": "写一个函数 fizzbuzz(n)，n 为 3 的倍数返回 'Fizz'，5 的倍数返回 'Buzz'，同时是两者返回 'FizzBuzz'，否则返回 n。",
        "test_cases": "assert fizzbuzz(3) == 'Fizz'\nassert fizzbuzz(5) == 'Buzz'\nassert fizzbuzz(15) == 'FizzBuzz'\nassert fizzbuzz(7) == 7",
        "xp_reward": 25,
    },
    {
        "task": "写一个函数 factorial(n)，返回 n 的阶乘（n!）。",
        "test_cases": "assert factorial(0) == 1\nassert factorial(5) == 120\nassert factorial(1) == 1",
        "xp_reward": 25,
    },
    {
        "task": "写一个函数 max_of_three(a, b, c)，返回三个数中最大的。",
        "test_cases": "assert max_of_three(1,2,3) == 3\nassert max_of_three(5,5,1) == 5\nassert max_of_three(-1,-2,-3) == -1",
        "xp_reward": 20,
    },
    {
        "task": "写一个函数 count_vowels(s)，返回字符串中元音字母（a/e/i/o/u）的数量，忽略大小写。",
        "test_cases": "assert count_vowels('hello') == 2\nassert count_vowels('AEIOU') == 5\nassert count_vowels('xyz') == 0",
        "xp_reward": 25,
    },
    {
        "task": "写一个函数 is_prime(n)，返回 n 是否为质数（n>1 且只能被 1 和自身整除）。",
        "test_cases": "assert is_prime(2) == True\nassert is_prime(4) == False\nassert is_prime(17) == True\nassert is_prime(1) == False",
        "xp_reward": 30,
    },
    {
        "task": "写一个函数 is_palindrome(s)，判断字符串是否回文（忽略大小写）。",
        "test_cases": "assert is_palindrome('racecar') == True\nassert is_palindrome('noon') == True\nassert is_palindrome('hello') == False",
        "xp_reward": 25,
    },
    {
        "task": "写一个函数 flatten_once(nested)，将嵌套列表拍平一层（如 [[1,2],[3]] → [1,2,3]）。",
        "test_cases": "assert flatten_once([[1,2],[3]]) == [1,2,3]\nassert flatten_once([[],[]]) == []\nassert flatten_once([1,[2]]) == [1,2]",
        "xp_reward": 30,
    },
    {
        "task": "写一个函数 is_sorted(nums)，判断列表是否已按非递减排序。",
        "test_cases": "assert is_sorted([1,2,3]) == True\nassert is_sorted([3,1]) == False\nassert is_sorted([]) == True",
        "xp_reward": 20,
    },
    {
        "task": "写一个函数 string_lengths(words)，返回每个字符串的长度列表。",
        "test_cases": "assert string_lengths(['a','bb','ccc']) == [1,2,3]\nassert string_lengths([]) == []",
        "xp_reward": 20,
    },
]


def seed_badges(db: Session) -> None:
    """幂等插入徽章定义。"""
    inserted = 0
    for b in BADGES:
        exists = db.query(Badge).filter(Badge.code == b["code"]).first()
        if exists is None:
            db.add(Badge(**b))
            inserted += 1
    if inserted:
        db.commit()
    logger.info("Gamification badges seeded: %d inserted", inserted)


def seed_daily_challenges(db: Session) -> None:
    """幂等种子未来 CHALLENGE_DAYS 天的每日挑战（题库循环）。"""
    inserted = 0
    today = datetime.date.today()
    for offset in range(CHALLENGE_DAYS):
        day = today + datetime.timedelta(days=offset)
        exists = db.query(DailyChallenge).filter(DailyChallenge.date == day).first()
        if exists is not None:
            continue  # 该日已有
        template = DAILY_CHALLENGES[offset % len(DAILY_CHALLENGES)]
        db.add(
            DailyChallenge(
                date=day,
                task=template["task"],
                test_cases=template["test_cases"],
                xp_reward=template["xp_reward"],
                is_active=True,
            )
        )
        inserted += 1
    if inserted:
        db.commit()
    logger.info("Gamification daily challenges seeded: %d inserted", inserted)