class PreScaler:

    def fit(self, X, y):
        return self

    def transform(self, X):
        X = X.mul(X['n_games'].fillna(1), axis=0)
        X = X.mul(X['chance_of_playing_next_round'].fillna(100)/100, axis=0)
        return X
