# Journaling Agent Workflow

## 📝 **Complete Journal Entry Workflow**

When you submit a journal entry, the journaling agent executes tools in this exact order:

### **Step 1: `standardize_journal_text`**
- **Input**: Raw journal text from user
- **Action**: Converts raw text to structured JSON format
- **Output**: Standardized entry with empowerment focus
- **JSON Structure**:
  ```json
  {
    "date": "YYYY-MM-DD",
    "mood": "primary emotional state", 
    "keyEvents": "brief external events",
    "reflection": "focus on internal thoughts, beliefs, and personal power"
  }
  ```

### **Step 2: `generate_journal_insights`**
- **Input**: Standardized entry from Step 1
- **Action**: Analyzes patterns for internal empowerment
- **Output**: Insights focusing on self-created beliefs
- **JSON Structure**:
  ```json
  {
    "sentiment": "negative|neutral|positive",
    "emotion": "primary emotion detected",
    "intensity": "1-10 scale",
    "themes": ["internal_theme1", "internal_theme2"],
    "triggers": ["internal_trigger1", "internal_trigger2"]
  }
  ```

### **Step 3: `generate_reflection_question`**
- **Input**: Standardized entry + insights from Steps 1-2
- **Action**: Creates ONE empowering question
- **Output**: Question that shifts focus from external to internal power
- **Format**: "What internal belief/thought/power can you explore about [situation]?"

### **Step 4: `store_journal_entry`**
- **Input**: All data from Steps 1-3
- **Action**: Saves to Firebase Firestore + generates embeddings
- **Output**: Journal ID and embedding ID
- **Storage**: 
  - Firestore: Raw text, standardized entry, insights
  - Pinecone: Vector embeddings for trend analysis

### **Step 5: `update_consistency_tracking`**
- **Input**: User ID and journal completion
- **Action**: Updates daily journaling metrics
- **Output**: Consistency statistics (streak, count)

### **Step 6: `trigger_mental_orchestrator`**
- **Input**: Journal ID and session data
- **Action**: Notifies Mental Orchestrator for mind map updates
- **Output**: Coordination result for pattern analysis

## 🎯 **Expected User Experience**

1. **User writes**: Raw journal text about their day/thoughts
2. **Agent standardizes**: Converts to empowerment-focused structure
3. **Agent analyzes**: Identifies internal patterns and themes
4. **Agent questions**: Provides ONE reflection question for growth
5. **Agent stores**: Saves everything for future trend analysis
6. **Agent tracks**: Updates consistency metrics
7. **Agent coordinates**: Triggers mind map pattern updates

## ⚡ **Success Indicators**

- ✅ Each tool returns structured `JournalingToolResult`
- ✅ Session state preserved between tools
- ✅ Empowerment language throughout
- ✅ Vector embeddings stored in Pinecone
- ✅ Mind map coordination triggered

## 🚨 **Error Handling**

If any step fails:
- Tool returns error with specific details
- Suggests next actions (retry, check input, etc.)
- Session state preserved for recovery
- User gets clear feedback on what went wrong 