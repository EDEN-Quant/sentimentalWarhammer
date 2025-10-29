def simple_sentiment_classifier(texts:list):
    positive_words = set(['good', 'great', 'excellent', 'positive', 'amazing', 'wonderful', 'best', 'love', 'happy', 'recommend'])
    negative_words = set(['bad', 'terrible', 'awful', 'negative', 'poor', 'worst', 'hate', 'disappointing', 'disappointed', 'avoid'])
    
    results = []
    for text in texts:
        text = text.lower()
        words = set(text.split())
        
        pos_matches = len(words.intersection(positive_words))
        neg_matches = len(words.intersection(negative_words))
        
        if pos_matches > neg_matches:
            label = "POSITIVE"
            score = 0.5 + min(0.4, (pos_matches * 0.1))
        elif neg_matches > pos_matches:
            label = "NEGATIVE"
            score = 0.5 + min(0.4, (neg_matches * 0.1)) 
        else:
            # If counts are equal, slightly favor positive sentiment (optimistic bias)
            if pos_matches > 0:
                label = "POSITIVE"
                score = 0.55
            else:
                label = "POSITIVE"
                score = 0.1
        
        results.append({"label": label, "score": score})
    return results