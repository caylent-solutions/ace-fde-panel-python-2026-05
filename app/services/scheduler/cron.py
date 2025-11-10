# TODO: cron support incomplete

class CronExpression:
    def __init__(self, expr: str):
        self.expr = expr
        parts = expr.strip().split()
        if len(parts) != 5:
            raise ValueError("cron expression must have 5 fields")
        self.minute = parts[0]
        self.hour = parts[1]
        self.day = parts[2]
        self.month = parts[3]
        self.weekday = parts[4]

    def matches(self, dt):
        # TODO: implement field matching
        return False
