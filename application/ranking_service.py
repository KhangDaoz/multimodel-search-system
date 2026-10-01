class RankingService:
    def rank(self, candidates, top_k=5):
        if top_k < 1:
            raise ValueError('top_k must be positive')
        # Primary relevance score; deterministic ID tie-break.
        ranked = sorted(candidates, key=lambda item: (-item[1], item[0]['id']))
        return [{'product':p, 'score':round(float(s),6)} for p,s in ranked[:top_k]]
