import numpy as np
from sklearn.linear_model import LinearRegression


class MLPredictor:

    @staticmethod
    def predict_next_weight(data):

        """
        data = [(date, weight, volume), ...]
        """

        if len(data) < 3:
            return "Need more data"

        # Convert dates to numeric index
        X = np.array(range(len(data))).reshape(-1, 1)

        # Weight values
        y = np.array([d[1] for d in data])

        # Train model
        model = LinearRegression()
        model.fit(X, y)

        # Predict next workout weight
        next_index = np.array([[len(data)]])
        prediction = model.predict(next_index)

        return round(float(prediction[0]), 2)