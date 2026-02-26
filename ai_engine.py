class AIEngine:

    @staticmethod
    def suggest_next_weight(data):

        if len(data) < 2:
            return "Add more workout data"

        weights = [d[1] for d in data]

        # Simple AI logic simulation
        avg_increase = sum(
            weights[i] - weights[i-1]
            for i in range(1, len(weights))
        ) / (len(weights)-1)

        next_weight = weights[-1] + avg_increase

        if next_weight < weights[-1]:
            next_weight = weights[-1] + 1

        return round(next_weight, 2)