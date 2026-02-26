class Calculations:

    @staticmethod
    def calculate_volume(weight, sets, reps):
        return weight * sets * reps

    @staticmethod
    def average_weight(data):
        if not data:
            return 0
        return sum(d[1] for d in data) / len(data)

    @staticmethod
    def total_volume(data):
        return sum(d[2] for d in data)