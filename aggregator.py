import streamlit as st
import re
import json
import os
from pathlib import Path

def parse_md_file(content):
    """Parse markdown file and extract questions"""
    questions = []
    
    # Split by question numbers
    question_blocks = re.split(r'\n(?=\d+\.)', content)
    
    for block in question_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # Extract question
        question_line = lines[0]
        question_match = re.match(r'^\d+\.\s*(.*)', question_line)
        if not question_match:
            continue
            
        question_text = question_match.group(1)
        
        # Extract options
        options = []
        answer_line = ""
        
        for line in lines[1:]:
            line = line.strip()
            if line.startswith('- '):
                # Extract option
                option_match = re.match(r'- ([A-D])\.\s*(.*)', line)
                if option_match:
                    options.append({
                        'letter': option_match.group(1),
                        'text': option_match.group(2)
                    })
            elif 'Correct answer:' in line:
                answer_match = re.search(r'Correct answer:\s*([A-D])', line)
                if answer_match:
                    answer_line = answer_match.group(1)
        
        if question_text and len(options) >= 2 and answer_line:
            questions.append({
                'question': question_text,
                'options': options,
                'correct_answer': answer_line
            })
    
    return questions

def main():
    st.set_page_config(page_title="AWS Quiz - Question Aggregator", layout="wide")
    
    st.title("🔄 AWS Quiz Question Aggregator")
    st.markdown("Upload your markdown files to create a question database")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Select markdown files", 
        type=['md'], 
        accept_multiple_files=True,
        help="Upload all your AWS quiz markdown files"
    )
    
    if uploaded_files:
        st.success(f"📁 {len(uploaded_files)} files uploaded")
        
        # Process files button
        if st.button("🔄 Process Files and Create Question Database", type="primary"):
            all_questions = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Read file content
                content = uploaded_file.read().decode('utf-8')
                
                # Parse questions
                questions = parse_md_file(content)
                all_questions.extend(questions)
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("Saving question database...")
            
            # Save to JSON file
            os.makedirs('data', exist_ok=True)
            with open('data/questions_db.json', 'w', encoding='utf-8') as f:
                json.dump(all_questions, f, indent=2, ensure_ascii=False)
            
            progress_bar.progress(1.0)
            status_text.text("✅ Complete!")
            
            # Display summary
            st.success(f"🎉 Successfully processed {len(all_questions)} questions!")
            
            # Show sample questions
            if st.checkbox("📋 Show sample questions"):
                st.subheader("Sample Questions Preview")
                
                for i, q in enumerate(all_questions[:3]):
                    with st.expander(f"Question {i+1}"):
                        st.write(f"**Q:** {q['question']}")
                        for opt in q['options']:
                            st.write(f"- {opt['letter']}. {opt['text']}")
                        st.write(f"**Correct Answer:** {q['correct_answer']}")
    
    # Check if database exists
    if os.path.exists('data/questions_db.json'):
        st.markdown("---")
        st.info("✅ Question database exists and ready to use!")
        
        # Load and show stats
        with open('data/questions_db.json', 'r', encoding='utf-8') as f:
            questions = json.load(f)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Questions", len(questions))
        with col2:
            st.metric("Database Status", "Ready")
        with col3:
            if st.button("🗑️ Clear Database"):
                os.remove('data/questions_db.json')
                st.rerun()

if __name__ == "__main__":
    main()