import json
import os
from django.conf import settings


class SymptomAnalyzer:
    def __init__(self):
        self.data = self._load_symptom_data()

    def _load_symptom_data(self):
        """Load symptom data from JSON file"""
        json_path = os.path.join(
            settings.BASE_DIR, 'symptom_checker', 'data', 'symptoms.json'
        )
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'symptoms': {}, 'specialties': {}, 'urgency_levels': {}}

    def analyze(self, user_input):
        """Analyze user symptoms and return recommendations"""
        user_input_lower = user_input.lower()
        matches = []
        
        # Check each symptom category
        for symptom_id, symptom_data in self.data.get('symptoms', {}).items():
            keywords = symptom_data.get('keywords', [])
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    matches.append({
                        'symptom_id': symptom_id,
                        'keyword_matched': keyword,
                        'specialty': symptom_data.get('specialty'),
                        'urgency': symptom_data.get('urgency'),
                        'advice': symptom_data.get('advice')
                    })
                    break  # Only count each symptom category once
        
        if not matches:
            return {
                'has_matches': False,
                'matches': [],
                'primary_specialty': 'general_physician',
                'specialty_info': self.data.get('specialties', {}).get('general_physician', {}),
                'urgency': 'low',
                'urgency_info': self.data.get('urgency_levels', {}).get('low', {}),
                'general_advice': "Based on your description, we recommend consulting a General Physician for a comprehensive evaluation. They can provide proper diagnosis and refer you to a specialist if needed."
            }
        
        # Determine primary recommendation based on highest urgency
        urgency_priority = {'high': 3, 'medium': 2, 'low': 1}
        matches.sort(key=lambda x: urgency_priority.get(x['urgency'], 0), reverse=True)
        
        primary_match = matches[0]
        specialty_key = primary_match['specialty']
        urgency_key = primary_match['urgency']
        
        return {
            'has_matches': True,
            'matches': matches,
            'primary_specialty': specialty_key,
            'specialty_info': self.data.get('specialties', {}).get(specialty_key, {}),
            'urgency': urgency_key,
            'urgency_info': self.data.get('urgency_levels', {}).get(urgency_key, {}),
            'general_advice': primary_match['advice']
        }

    def get_all_specialties(self):
        """Return all available specialties"""
        return self.data.get('specialties', {})

    def get_specialty_symptoms(self, specialty):
        """Return all symptoms associated with a specialty"""
        symptoms = []
        for symptom_id, symptom_data in self.data.get('symptoms', {}).items():
            if symptom_data.get('specialty') == specialty:
                symptoms.append({
                    'id': symptom_id,
                    'keywords': symptom_data.get('keywords', []),
                    'advice': symptom_data.get('advice')
                })
        return symptoms
