"""
Sample Excel interview questions organized by category and difficulty level
"""

from typing import Dict, List, Any

# Question categories
QUESTION_CATEGORIES = [
    "Basic Functions",
    "Advanced Functions", 
    "Data Analysis",
    "PivotTables",
    "Charts and Visualization",
    "Data Validation",
    "Macros and VBA",
    "Problem Solving",
    "Formulas and Logic",
    "Data Management"
]

# Sample questions organized by difficulty and category
SAMPLE_QUESTIONS: Dict[str, List[Dict[str, Any]]] = {
    "Beginner": [
        {
            "question": "How would you use the SUM function to calculate the total of a range of cells? Can you explain the syntax?",
            "category": "Basic Functions",
            "difficulty": "Beginner",
            "expected_topics": ["SUM function", "cell references", "syntax"],
            "follow_up_hints": ["What about non-contiguous ranges?", "How does SUMIF differ?"]
        },
        {
            "question": "Explain how to create a simple chart in Excel. What steps would you follow?",
            "category": "Charts and Visualization", 
            "difficulty": "Beginner",
            "expected_topics": ["chart creation", "data selection", "chart types"],
            "follow_up_hints": ["How do you modify chart elements?", "What chart type is best for what data?"]
        },
        {
            "question": "How do you apply basic data validation to ensure only numbers between 1 and 100 are entered in a cell?",
            "category": "Data Validation",
            "difficulty": "Beginner", 
            "expected_topics": ["data validation", "input restrictions", "error messages"],
            "follow_up_hints": ["What about custom validation messages?", "How to create dropdown lists?"]
        },
        {
            "question": "What is the difference between relative and absolute cell references? Can you give examples?",
            "category": "Formulas and Logic",
            "difficulty": "Beginner",
            "expected_topics": ["relative references", "absolute references", "$A$1 vs A1"],
            "follow_up_hints": ["When would you use mixed references?", "What happens when copying formulas?"]
        }
    ],
    
    "Intermediate": [
        {
            "question": "How would you use VLOOKUP to find data in a large dataset? Can you explain the syntax and when you might use it?",
            "category": "Advanced Functions",
            "difficulty": "Intermediate",
            "expected_topics": ["VLOOKUP", "syntax", "data lookup", "approximate vs exact match"],
            "follow_up_hints": ["What are VLOOKUP limitations?", "How does INDEX-MATCH compare?"]
        },
        {
            "question": "Describe how to create a PivotTable and what insights it can provide for sales data analysis.",
            "category": "PivotTables",
            "difficulty": "Intermediate",
            "expected_topics": ["PivotTable creation", "rows", "columns", "values", "filters"],
            "follow_up_hints": ["How do you handle calculated fields?", "What about grouping data?"]
        },
        {
            "question": "How would you use conditional formatting to highlight cells based on specific criteria?",
            "category": "Data Analysis",
            "difficulty": "Intermediate",
            "expected_topics": ["conditional formatting", "rules", "cell highlighting", "data bars"],
            "follow_up_hints": ["How to create custom formulas for formatting?", "What about icon sets?"]
        },
        {
            "question": "Explain how to use the IF function with nested conditions. Can you provide a practical example?",
            "category": "Formulas and Logic",
            "difficulty": "Intermediate",
            "expected_topics": ["IF function", "nested IF", "logical operators", "AND/OR functions"],
            "follow_up_hints": ["What about IFS function?", "How to handle complex decision trees?"]
        }
    ],
    
    "Advanced": [
        {
            "question": "How would you use array formulas to perform complex calculations across multiple ranges simultaneously?",
            "category": "Advanced Functions",
            "difficulty": "Advanced", 
            "expected_topics": ["array formulas", "Ctrl+Shift+Enter", "dynamic arrays", "SUMPRODUCT"],
            "follow_up_hints": ["What about dynamic array functions?", "How do FILTER and UNIQUE work?"]
        },
        {
            "question": "Describe a scenario where you would create a macro to automate a repetitive task. How would you approach it?",
            "category": "Macros and VBA",
            "difficulty": "Advanced",
            "expected_topics": ["macro recording", "VBA", "automation", "repetitive tasks"],
            "follow_up_hints": ["What about error handling in VBA?", "How to make macros more efficient?"]
        },
        {
            "question": "How would you design a dashboard that automatically updates when source data changes?",
            "category": "Data Analysis",
            "difficulty": "Advanced",
            "expected_topics": ["dynamic dashboards", "named ranges", "data connections", "refresh"],
            "follow_up_hints": ["What about real-time data sources?", "How to optimize performance?"]
        },
        {
            "question": "Explain how you would use Power Query to clean and transform messy data from multiple sources.",
            "category": "Data Management",
            "difficulty": "Advanced",
            "expected_topics": ["Power Query", "data transformation", "merging data", "cleaning"],
            "follow_up_hints": ["What about custom functions in M language?", "How to handle errors in transformation?"]
        }
    ],
    
    "Expert": [
        {
            "question": "How would you optimize Excel performance when working with large datasets (1M+ rows)?",
            "category": "Data Management",
            "difficulty": "Expert",
            "expected_topics": ["performance optimization", "large datasets", "memory management", "calculation modes"],
            "follow_up_hints": ["What about Power Pivot?", "How does Excel handle big data limitations?"]
        },
        {
            "question": "Describe how you would implement a complex financial model with scenario analysis and sensitivity testing.",
            "category": "Problem Solving",
            "difficulty": "Expert",
            "expected_topics": ["financial modeling", "scenario analysis", "data tables", "goal seek"],
            "follow_up_hints": ["What about Monte Carlo simulation?", "How to validate model accuracy?"]
        },
        {
            "question": "How would you create a custom Excel add-in to extend functionality for your team?",
            "category": "Macros and VBA",
            "difficulty": "Expert",
            "expected_topics": ["Excel add-ins", "COM add-ins", "custom functions", "deployment"],
            "follow_up_hints": ["What about VSTO vs VBA?", "How to handle version compatibility?"]
        },
        {
            "question": "Explain how you would integrate Excel with external APIs to automatically fetch and update data.",
            "category": "Data Management", 
            "difficulty": "Expert",
            "expected_topics": ["API integration", "web queries", "JSON parsing", "automation"],
            "follow_up_hints": ["What about authentication?", "How to handle rate limiting?"]
        }
    ]
}

# Scenario-based questions that might require Excel files
SCENARIO_QUESTIONS = [
    {
        "question": "You have been given a sales dataset with inconsistent formatting. How would you clean and analyze it to identify top-performing products?",
        "category": "Problem Solving",
        "difficulty": "Intermediate",
        "requires_file": False,
        "expected_topics": ["data cleaning", "text functions", "analysis", "ranking"],
        "follow_up_hints": ["What functions would you use for cleaning?", "How would you handle duplicates?"]
    },
    {
        "question": "A manager needs a dynamic report that shows monthly trends and can be filtered by region and product category. How would you build this?",
        "category": "Data Analysis",
        "difficulty": "Advanced",
        "requires_file": False,
        "expected_topics": ["dynamic reports", "slicers", "PivotTables", "charts"],
        "follow_up_hints": ["How would you make it user-friendly?", "What about printing considerations?"]
    }
]

def get_questions_by_level(experience_level: str) -> List[Dict[str, Any]]:
    """Get questions appropriate for the given experience level"""
    return SAMPLE_QUESTIONS.get(experience_level, SAMPLE_QUESTIONS["Intermediate"])

def get_questions_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all questions from a specific category"""
    questions = []
    for level_questions in SAMPLE_QUESTIONS.values():
        for question in level_questions:
            if question["category"] == category:
                questions.append(question)
    return questions

def get_random_question(experience_level: str, excluded_categories: List[str] = None) -> Dict[str, Any]:
    """Get a random question for the given level, excluding specified categories"""
    import random
    
    available_questions = get_questions_by_level(experience_level)
    
    if excluded_categories:
        available_questions = [
            q for q in available_questions 
            if q["category"] not in excluded_categories
        ]
    
    if not available_questions:
        # Fallback to any question if no suitable ones found
        available_questions = SAMPLE_QUESTIONS["Intermediate"]
    
    return random.choice(available_questions)
