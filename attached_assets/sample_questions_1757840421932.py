"""
Sample Excel interview questions organized by category and difficulty level
"""
from typing import Optional

QUESTION_CATEGORIES = [
    "Basic Operations",
    "Formulas and Functions", 
    "Data Analysis",
    "Data Visualization",
    "Advanced Features",
    "Data Management",
    "Troubleshooting",
    "Best Practices"
]

SAMPLE_QUESTIONS = [
    # Basic Operations
    {
        "question": "How would you quickly navigate to the last row of data in a large Excel spreadsheet? Can you explain multiple methods?",
        "category": "Basic Operations",
        "difficulty": "Beginner",
        "expected_topics": ["keyboard shortcuts", "Ctrl+End", "Ctrl+Down", "navigation"],
        "follow_up_hints": ["Ctrl+Shift combinations", "Name Box usage"]
    },
    {
        "question": "Explain the difference between relative and absolute cell references. When would you use each type?",
        "category": "Basic Operations", 
        "difficulty": "Beginner",
        "expected_topics": ["relative references", "absolute references", "$", "cell addressing"],
        "follow_up_hints": ["mixed references", "copying formulas"]
    },
    {
        "question": "How do you freeze panes in Excel and why would you want to do this?",
        "category": "Basic Operations",
        "difficulty": "Beginner", 
        "expected_topics": ["freeze panes", "View tab", "headers", "scrolling"],
        "follow_up_hints": ["split panes", "freeze first column only"]
    },
    
    # Formulas and Functions
    {
        "question": "Explain how VLOOKUP works and provide an example of when you would use it. What are its limitations?",
        "category": "Formulas and Functions",
        "difficulty": "Intermediate",
        "expected_topics": ["VLOOKUP", "lookup_value", "table_array", "col_index_num", "exact match"],
        "follow_up_hints": ["INDEX-MATCH alternative", "approximate match"]
    },
    {
        "question": "How would you count cells that meet multiple criteria? Can you explain different approaches?",
        "category": "Formulas and Functions",
        "difficulty": "Intermediate",
        "expected_topics": ["COUNTIFS", "multiple criteria", "arrays", "conditions"],
        "follow_up_hints": ["SUMIFS", "AVERAGEIFS", "array formulas"]
    },
    {
        "question": "What's the difference between CONCATENATE and the & operator? When would you use each?",
        "category": "Formulas and Functions",
        "difficulty": "Beginner",
        "expected_topics": ["CONCATENATE", "ampersand", "text joining", "string manipulation"],
        "follow_up_hints": ["CONCAT function", "TEXTJOIN"]
    },
    {
        "question": "How do you use INDEX and MATCH together? Why might this be preferable to VLOOKUP?",
        "category": "Formulas and Functions",
        "difficulty": "Advanced",
        "expected_topics": ["INDEX", "MATCH", "flexibility", "left lookup", "performance"],
        "follow_up_hints": ["two-way lookup", "approximate match"]
    },
    
    # Data Analysis
    {
        "question": "Walk me through creating a pivot table. What insights can pivot tables provide?",
        "category": "Data Analysis",
        "difficulty": "Intermediate",
        "expected_topics": ["pivot tables", "summarization", "grouping", "fields", "values"],
        "follow_up_hints": ["calculated fields", "slicers", "pivot charts"]
    },
    {
        "question": "How would you identify and remove duplicate data in Excel? What methods are available?",
        "category": "Data Analysis",
        "difficulty": "Beginner",
        "expected_topics": ["duplicates", "Remove Duplicates", "conditional formatting", "advanced filter"],
        "follow_up_hints": ["COUNTIF for identification", "unique values"]
    },
    {
        "question": "Explain how to use Excel's Goal Seek feature. Can you provide a practical example?",
        "category": "Data Analysis",
        "difficulty": "Advanced",
        "expected_topics": ["Goal Seek", "what-if analysis", "target value", "variable cell"],
        "follow_up_hints": ["Solver add-in", "Data Table"]
    },
    {
        "question": "How do you perform a sensitivity analysis or what-if analysis in Excel?",
        "category": "Data Analysis",
        "difficulty": "Advanced",
        "expected_topics": ["what-if analysis", "Data Table", "scenarios", "sensitivity"],
        "follow_up_hints": ["Scenario Manager", "Monte Carlo simulation"]
    },
    
    # Data Visualization
    {
        "question": "What factors do you consider when choosing the right chart type for your data?",
        "category": "Data Visualization",
        "difficulty": "Intermediate",
        "expected_topics": ["chart types", "data relationships", "audience", "purpose"],
        "follow_up_hints": ["bar vs column", "line charts", "scatter plots"]
    },
    {
        "question": "How do you create a dynamic chart that updates automatically when data changes?",
        "category": "Data Visualization", 
        "difficulty": "Advanced",
        "expected_topics": ["dynamic charts", "named ranges", "OFFSET", "dynamic ranges"],
        "follow_up_hints": ["Tables", "chart data source"]
    },
    {
        "question": "Explain how to create and use sparklines in Excel. What are their advantages?",
        "category": "Data Visualization",
        "difficulty": "Intermediate",
        "expected_topics": ["sparklines", "mini charts", "trends", "Insert tab"],
        "follow_up_hints": ["sparkline types", "formatting options"]
    },
    
    # Advanced Features
    {
        "question": "What are Excel Tables and what advantages do they offer over regular ranges?",
        "category": "Advanced Features",
        "difficulty": "Intermediate",
        "expected_topics": ["Excel Tables", "structured references", "filtering", "formatting"],
        "follow_up_hints": ["table expansion", "calculated columns", "slicers"]
    },
    {
        "question": "How do you create and use named ranges in Excel? What are the benefits?",
        "category": "Advanced Features",
        "difficulty": "Intermediate", 
        "expected_topics": ["named ranges", "Name Manager", "formulas", "readability"],
        "follow_up_hints": ["dynamic named ranges", "scope"]
    },
    {
        "question": "Explain the concept of array formulas in Excel. Can you provide an example?",
        "category": "Advanced Features",
        "difficulty": "Advanced",
        "expected_topics": ["array formulas", "Ctrl+Shift+Enter", "multiple calculations", "arrays"],
        "follow_up_hints": ["dynamic arrays", "spill range"]
    },
    {
        "question": "What is Power Query and how does it help with data preparation?",
        "category": "Advanced Features",
        "difficulty": "Advanced",
        "expected_topics": ["Power Query", "data transformation", "ETL", "Data tab"],
        "follow_up_hints": ["M language", "query steps", "refresh"]
    },
    
    # Data Management
    {
        "question": "How do you protect sensitive data in Excel workbooks? What security options are available?",
        "category": "Data Management",
        "difficulty": "Intermediate",
        "expected_topics": ["worksheet protection", "workbook protection", "passwords", "cell locking"],
        "follow_up_hints": ["range protection", "digital signatures"]
    },
    {
        "question": "Explain data validation in Excel. How would you create dropdown lists?",
        "category": "Data Management",
        "difficulty": "Beginner",
        "expected_topics": ["data validation", "dropdown lists", "input restrictions", "error messages"],
        "follow_up_hints": ["custom validation", "dependent dropdowns"]
    },
    {
        "question": "How do you handle large datasets in Excel efficiently? What are the limitations?",
        "category": "Data Management",
        "difficulty": "Advanced",
        "expected_topics": ["large datasets", "performance", "row limits", "memory"],
        "follow_up_hints": ["Power Pivot", "external data connections"]
    },
    
    # Troubleshooting
    {
        "question": "A formula is returning #N/A error. What could be causing this and how would you fix it?",
        "category": "Troubleshooting",
        "difficulty": "Intermediate",
        "expected_topics": ["#N/A error", "lookup functions", "error handling", "IFERROR"],
        "follow_up_hints": ["data types", "spelling", "IFNA function"]
    },
    {
        "question": "What does #VALUE! error mean and how do you resolve it?",
        "category": "Troubleshooting", 
        "difficulty": "Beginner",
        "expected_topics": ["#VALUE! error", "data types", "text vs numbers", "format issues"],
        "follow_up_hints": ["VALUE function", "CLEAN function"]
    },
    {
        "question": "How do you audit and trace formula dependencies in Excel?",
        "category": "Troubleshooting",
        "difficulty": "Advanced",
        "expected_topics": ["formula auditing", "trace precedents", "trace dependents", "error checking"],
        "follow_up_hints": ["Formula tab", "show formulas", "circular references"]
    },
    
    # Best Practices
    {
        "question": "What are some Excel best practices for organizing and structuring data?",
        "category": "Best Practices",
        "difficulty": "Intermediate",
        "expected_topics": ["data organization", "headers", "consistent formatting", "documentation"],
        "follow_up_hints": ["one data type per column", "avoid merged cells", "backup"]
    },
    {
        "question": "How do you make your Excel models more maintainable and user-friendly?",
        "category": "Best Practices",
        "difficulty": "Advanced",
        "expected_topics": ["documentation", "named ranges", "clear structure", "error handling"],
        "follow_up_hints": ["version control", "input validation", "instructions"]
    },
    {
        "question": "What strategies do you use to ensure data accuracy and reduce errors in Excel?",
        "category": "Best Practices",
        "difficulty": "Intermediate", 
        "expected_topics": ["data validation", "error checking", "testing", "verification"],
        "follow_up_hints": ["cross-checking", "formula auditing", "peer review"]
    }
]

# Question pools by experience level
BEGINNER_QUESTIONS = [q for q in SAMPLE_QUESTIONS if q["difficulty"] == "Beginner"]
INTERMEDIATE_QUESTIONS = [q for q in SAMPLE_QUESTIONS if q["difficulty"] == "Intermediate"] 
ADVANCED_QUESTIONS = [q for q in SAMPLE_QUESTIONS if q["difficulty"] == "Advanced"]

# All questions that are suitable for any level
ALL_LEVEL_QUESTIONS = SAMPLE_QUESTIONS

def get_questions_by_category(category: str) -> list:
    """Get all questions for a specific category"""
    return [q for q in SAMPLE_QUESTIONS if q["category"] == category]

def get_questions_by_difficulty(difficulty: str) -> list:
    """Get all questions for a specific difficulty level"""
    return [q for q in SAMPLE_QUESTIONS if q["difficulty"] == difficulty]

def get_random_question(category: Optional[str] = None, difficulty: Optional[str] = None) -> dict:
    """Get a random question, optionally filtered by category and/or difficulty"""
    import random
    
    filtered_questions = SAMPLE_QUESTIONS
    
    if category:
        filtered_questions = [q for q in filtered_questions if q["category"] == category]
    
    if difficulty:
        filtered_questions = [q for q in filtered_questions if q["difficulty"] == difficulty]
    
    if not filtered_questions:
        return random.choice(SAMPLE_QUESTIONS)
    
    return random.choice(filtered_questions)

def get_progressive_question_set(experience_level: str, num_questions: int = 8) -> list:
    """Get a progressive set of questions based on experience level"""
    import random
    
    if "beginner" in experience_level.lower():
        beginner_ratio = 0.6
        intermediate_ratio = 0.3
        advanced_ratio = 0.1
    elif "intermediate" in experience_level.lower():
        beginner_ratio = 0.2
        intermediate_ratio = 0.6
        advanced_ratio = 0.2
    else:  # Advanced
        beginner_ratio = 0.1
        intermediate_ratio = 0.4
        advanced_ratio = 0.5
    
    # Calculate number of questions per difficulty
    num_beginner = max(1, int(num_questions * beginner_ratio))
    num_intermediate = max(1, int(num_questions * intermediate_ratio))
    num_advanced = num_questions - num_beginner - num_intermediate
    
    questions = []
    
    # Add beginner questions
    if num_beginner > 0:
        beginner_sample = random.sample(BEGINNER_QUESTIONS, min(num_beginner, len(BEGINNER_QUESTIONS)))
        questions.extend(beginner_sample)
    
    # Add intermediate questions
    if num_intermediate > 0:
        intermediate_sample = random.sample(INTERMEDIATE_QUESTIONS, min(num_intermediate, len(INTERMEDIATE_QUESTIONS)))
        questions.extend(intermediate_sample)
    
    # Add advanced questions
    if num_advanced > 0:
        advanced_sample = random.sample(ADVANCED_QUESTIONS, min(num_advanced, len(ADVANCED_QUESTIONS)))
        questions.extend(advanced_sample)
    
    # Shuffle the final set
    random.shuffle(questions)
    
    return questions

# Question metadata
QUESTION_METADATA = {
    "total_questions": len(SAMPLE_QUESTIONS),
    "categories": QUESTION_CATEGORIES,
    "difficulty_distribution": {
        "Beginner": len(BEGINNER_QUESTIONS),
        "Intermediate": len(INTERMEDIATE_QUESTIONS), 
        "Advanced": len(ADVANCED_QUESTIONS)
    },
    "category_distribution": {
        category: len(get_questions_by_category(category)) 
        for category in QUESTION_CATEGORIES
    }
}
