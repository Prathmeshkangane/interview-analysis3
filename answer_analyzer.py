"""
Answer Analyzer Module
Analyzes interview answers using NLP for content quality, relevance, and sentiment
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, List
import re


# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class AnswerAnalyzer:
    """Analyze interview answers for quality and relevance"""
    
    def __init__(self):
        """Initialize answer analyzer"""
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
    
    def analyze_answer(self, answer: str, question: str, 
                       expected_keywords: List[str] = None) -> Dict:
        """
        Comprehensive analysis of interview answer
        
        Args:
            answer: Candidate's answer
            question: Interview question
            expected_keywords: Optional list of expected keywords/topics
            
        Returns:
            Dictionary with analysis metrics
        """
        if not answer or not answer.strip():
            return self._get_empty_analysis()
        
        analysis = {
            'text_metrics': self._analyze_text_metrics(answer),
            'content_quality': self._analyze_content_quality(answer),
            'sentiment': self._analyze_sentiment(answer),
            'relevance': self._analyze_relevance(answer, question, expected_keywords),
            'clarity': self._analyze_clarity(answer),
            'professionalism': self._analyze_professionalism(answer),
            'overall_score': 0
        }
        
        # Calculate overall score
        analysis['overall_score'] = self._calculate_overall_score(analysis)
        
        return analysis
    
    def _analyze_text_metrics(self, text: str) -> Dict:
        """Analyze basic text metrics"""
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        # Filter out stopwords for content words
        content_words = [w for w in words if w.isalpha() and w not in self.stop_words]
        
        # Calculate average word length
        avg_word_length = sum(len(w) for w in content_words) / len(content_words) if content_words else 0
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'content_word_count': len(content_words),
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'unique_words': len(set(content_words)),
            'vocabulary_richness': len(set(content_words)) / len(content_words) if content_words else 0
        }
    
    def _analyze_content_quality(self, text: str) -> Dict:
        """Analyze content quality and depth"""
        blob = TextBlob(text)
        
        # Check for examples and specificity
        has_numbers = bool(re.search(r'\d+', text))
        has_examples = any(phrase in text.lower() for phrase in 
                          ['for example', 'for instance', 'such as', 'like when', 'specifically'])
        has_quantification = any(word in text.lower() for word in 
                                ['increased', 'decreased', 'improved', 'reduced', 'achieved', 'percent', '%'])
        
        # Check for action verbs (indicative of achievements)
        action_verbs = ['developed', 'created', 'implemented', 'designed', 'led', 
                       'managed', 'built', 'launched', 'improved', 'optimized']
        action_verb_count = sum(1 for verb in action_verbs if verb in text.lower())
        
        # Check for structure indicators
        has_structure = any(phrase in text.lower() for phrase in 
                           ['first', 'second', 'third', 'firstly', 'finally', 'in conclusion'])
        
        quality_score = 50  # Base score
        
        if has_numbers:
            quality_score += 10
        if has_examples:
            quality_score += 15
        if has_quantification:
            quality_score += 10
        if action_verb_count > 0:
            quality_score += min(15, action_verb_count * 5)
        if has_structure:
            quality_score += 10
        
        return {
            'quality_score': min(100, quality_score),
            'has_examples': has_examples,
            'has_quantification': has_quantification,
            'action_verbs_used': action_verb_count,
            'has_structure': has_structure,
            'subjectivity': blob.sentiment.subjectivity,
            'polarity': blob.sentiment.polarity
        }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment and emotional tone"""
        # VADER sentiment analysis
        vader_scores = self.sentiment_analyzer.polarity_scores(text)
        
        # TextBlob sentiment
        blob = TextBlob(text)
        
        # Determine overall sentiment
        compound_score = vader_scores['compound']
        if compound_score >= 0.05:
            overall_sentiment = 'positive'
        elif compound_score <= -0.05:
            overall_sentiment = 'negative'
        else:
            overall_sentiment = 'neutral'
        
        # Confidence level indicators
        confidence_words = ['confident', 'sure', 'certain', 'definitely', 'absolutely']
        uncertainty_words = ['maybe', 'perhaps', 'might', 'possibly', 'unsure', 'think', 'guess']
        
        confidence_count = sum(1 for word in confidence_words if word in text.lower())
        uncertainty_count = sum(1 for word in uncertainty_words if word in text.lower())
        
        confidence_score = 50 + (confidence_count * 10) - (uncertainty_count * 10)
        confidence_score = max(0, min(100, confidence_score))
        
        return {
            'overall_sentiment': overall_sentiment,
            'positive_score': vader_scores['pos'],
            'negative_score': vader_scores['neg'],
            'neutral_score': vader_scores['neu'],
            'compound_score': vader_scores['compound'],
            'confidence_level': confidence_score,
            'enthusiasm_score': max(0, min(100, (vader_scores['pos'] * 100)))
        }
    
    def _analyze_relevance(self, answer: str, question: str, 
                          expected_keywords: List[str] = None) -> Dict:
        """Analyze answer relevance to question"""
        answer_lower = answer.lower()
        question_lower = question.lower()
        
        # Extract question keywords
        question_words = word_tokenize(question_lower)
        question_keywords = [w for w in question_words if w.isalpha() and w not in self.stop_words]
        
        # Check keyword overlap
        answer_words = word_tokenize(answer_lower)
        answer_keywords = [w for w in answer_words if w.isalpha() and w not in self.stop_words]
        
        keyword_overlap = len(set(question_keywords) & set(answer_keywords))
        relevance_score = min(100, (keyword_overlap / len(question_keywords) * 100) if question_keywords else 50)
        
        # Check for expected keywords if provided
        expected_keyword_score = 0
        if expected_keywords:
            found_keywords = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
            expected_keyword_score = (found_keywords / len(expected_keywords) * 100) if expected_keywords else 0
            relevance_score = (relevance_score + expected_keyword_score) / 2
        
        # Check if answer directly addresses the question
        addresses_question = any(phrase in answer_lower for phrase in 
                                ['yes', 'no', 'i would', 'i have', 'my experience', 'in my role'])
        
        if addresses_question:
            relevance_score += 10
        
        return {
            'relevance_score': min(100, relevance_score),
            'keyword_overlap_count': keyword_overlap,
            'addresses_question': addresses_question,
            'expected_keywords_found': expected_keyword_score if expected_keywords else None
        }
    
    def _analyze_clarity(self, text: str) -> Dict:
        """Analyze clarity and coherence of answer"""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        # Calculate Flesch Reading Ease (simplified)
        # Higher score = easier to read (0-100)
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_syllables = sum(self._count_syllables(word) for word in words) / len(words) if words else 0
        
        flesch_score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables
        flesch_score = max(0, min(100, flesch_score))
        
        # Check for filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'actually', 'basically', 'literally']
        filler_count = sum(text.lower().count(filler) for filler in filler_words)
        
        # Check for transition words (indicates structure)
        transition_words = ['however', 'therefore', 'additionally', 'furthermore', 
                           'moreover', 'consequently', 'meanwhile']
        transition_count = sum(1 for trans in transition_words if trans in text.lower())
        
        clarity_score = flesch_score
        clarity_score -= (filler_count * 5)  # Penalty for fillers
        clarity_score += (transition_count * 3)  # Bonus for transitions
        clarity_score = max(0, min(100, clarity_score))
        
        return {
            'clarity_score': clarity_score,
            'readability_score': flesch_score,
            'filler_word_count': filler_count,
            'transition_word_count': transition_count,
            'coherence': 'high' if transition_count > 2 else 'medium' if transition_count > 0 else 'low'
        }
    
    def _analyze_professionalism(self, text: str) -> Dict:
        """Analyze professional tone and language"""
        text_lower = text.lower()
        
        # Check for professional language
        professional_phrases = ['in my experience', 'i believe', 'i demonstrated', 
                               'i achieved', 'i collaborated', 'i led', 'my role']
        professional_count = sum(1 for phrase in professional_phrases if phrase in text_lower)
        
        # Check for casual/informal language
        casual_words = ['gonna', 'wanna', 'kinda', 'sorta', 'yeah', 'stuff', 'things']
        casual_count = sum(1 for word in casual_words if word in text_lower)
        
        # Check for negative words
        negative_words = ['failed', 'couldn\'t', 'never', 'impossible', 'difficult']
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        # Calculate professionalism score
        prof_score = 70  # Base score
        prof_score += professional_count * 5
        prof_score -= casual_count * 10
        prof_score -= negative_count * 3
        prof_score = max(0, min(100, prof_score))
        
        return {
            'professionalism_score': prof_score,
            'professional_phrases': professional_count,
            'casual_language': casual_count,
            'negative_language': negative_count,
            'tone': 'professional' if prof_score > 70 else 'casual' if prof_score > 40 else 'needs improvement'
        }
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""
        word = word.lower()
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        
        # Adjust for silent e
        if word.endswith('e'):
            syllable_count -= 1
        
        # Ensure at least one syllable
        if syllable_count == 0:
            syllable_count = 1
        
        return syllable_count
    
    def _calculate_overall_score(self, analysis: Dict) -> float:
        """Calculate weighted overall score"""
        weights = {
            'content_quality': 0.30,
            'relevance': 0.25,
            'clarity': 0.20,
            'sentiment': 0.15,
            'professionalism': 0.10
        }
        
        scores = {
            'content_quality': analysis['content_quality']['quality_score'],
            'relevance': analysis['relevance']['relevance_score'],
            'clarity': analysis['clarity']['clarity_score'],
            'sentiment': analysis['sentiment']['confidence_level'],
            'professionalism': analysis['professionalism']['professionalism_score']
        }
        
        overall = sum(scores[key] * weights[key] for key in weights.keys())
        return round(overall, 2)
    
    def _get_empty_analysis(self) -> Dict:
        """Return empty analysis for no answer"""
        return {
            'text_metrics': {'word_count': 0},
            'content_quality': {'quality_score': 0},
            'sentiment': {'overall_sentiment': 'neutral', 'confidence_level': 0},
            'relevance': {'relevance_score': 0},
            'clarity': {'clarity_score': 0},
            'professionalism': {'professionalism_score': 0},
            'overall_score': 0
        }
    
    def get_feedback(self, analysis: Dict) -> List[str]:
        """
        Generate actionable feedback based on analysis
        
        Args:
            analysis: Analysis results
            
        Returns:
            List of feedback points
        """
        feedback = []
        
        # Content quality feedback
        if analysis['content_quality']['quality_score'] < 60:
            feedback.append("Consider providing more specific examples and quantifiable achievements")
        if not analysis['content_quality']['has_examples']:
            feedback.append("Include concrete examples to illustrate your points")
        
        # Relevance feedback
        if analysis['relevance']['relevance_score'] < 60:
            feedback.append("Make sure your answer directly addresses the question asked")
        
        # Clarity feedback
        if analysis['clarity']['filler_word_count'] > 3:
            feedback.append("Reduce use of filler words (um, uh, like) for clearer communication")
        if analysis['clarity']['clarity_score'] < 60:
            feedback.append("Organize your thoughts more clearly with better structure")
        
        # Sentiment feedback
        if analysis['sentiment']['confidence_level'] < 50:
            feedback.append("Speak with more confidence and conviction")
        if analysis['sentiment']['enthusiasm_score'] < 30:
            feedback.append("Show more enthusiasm and positive energy in your responses")
        
        # Professionalism feedback
        if analysis['professionalism']['professionalism_score'] < 60:
            feedback.append("Use more professional language and avoid casual expressions")
        
        # Length feedback
        if analysis['text_metrics']['word_count'] < 30:
            feedback.append("Provide more detailed responses (aim for 50-150 words)")
        elif analysis['text_metrics']['word_count'] > 200:
            feedback.append("Keep responses more concise and focused")
        
        if not feedback:
            feedback.append("Great answer! Keep up the good work!")
        
        return feedback


if __name__ == "__main__":
    # Test the answer analyzer
    print("Answer Analyzer Module - Test Mode")
    print("=" * 50)
    
    analyzer = AnswerAnalyzer()
    
    sample_question = "Tell me about a time when you had to solve a difficult technical problem."
    
    sample_answer = """
    In my previous role, I encountered a critical performance issue where our application 
    was experiencing 5-second load times. I led the investigation and discovered the root 
    cause was inefficient database queries. I implemented query optimization and caching, 
    which reduced load times by 80% to under 1 second. This improvement significantly 
    enhanced user experience and increased customer satisfaction scores by 25%.
    """
    
    print("\nAnalyzing sample answer...\n")
    
    analysis = analyzer.analyze_answer(sample_answer, sample_question)
    
    print(f"Overall Score: {analysis['overall_score']}/100\n")
    
    print("Detailed Analysis:")
    print(f"  Content Quality: {analysis['content_quality']['quality_score']}/100")
    print(f"  Relevance: {analysis['relevance']['relevance_score']}/100")
    print(f"  Clarity: {analysis['clarity']['clarity_score']}/100")
    print(f"  Confidence: {analysis['sentiment']['confidence_level']}/100")
    print(f"  Professionalism: {analysis['professionalism']['professionalism_score']}/100")
    
    print("\nFeedback:")
    feedback = analyzer.get_feedback(analysis)
    for i, point in enumerate(feedback, 1):
        print(f"  {i}. {point}")