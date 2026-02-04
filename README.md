# Quick Start Guide - AI Mock Interview System

## ⚡ Get Started in 5 Minutes

### Step 1: Install Python (if not installed)
Download from: https://www.python.org/downloads/
- Minimum version: Python 3.8
- Make sure to check "Add Python to PATH" during installation

### Step 2: Install Dependencies
```bash
# Open terminal/command prompt in project folder
pip install -r requirements.txt
```

### Step 3: Get API Key (Choose One)

**Option A: OpenAI (Recommended)**
1. Go to https://platform.openai.com/api-keys
2. Create account and generate API key
3. Copy the key

**Option B: Anthropic Claude**
1. Go to https://console.anthropic.com/
2. Create account and generate API key
3. Copy the key

### Step 4: Configure API Key
1. Copy `config.env.example` to `.env`
2. Open `.env` in text editor
3. Paste your API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

### Step 5: Run the Interview!
```bash
python interview_system.py
```

## 📝 Tips for Best Results

### Before Starting:
✅ Close other apps using camera/microphone
✅ Find a quiet room with good lighting
✅ Position camera at eye level
✅ Test your microphone volume
✅ Prepare your resume and job description files

### During Interview:
✅ Look at the camera when speaking
✅ Speak clearly and at moderate pace
✅ Take brief pauses between thoughts
✅ Use specific examples with numbers
✅ Keep answers 30-90 seconds long

### Answer Structure (STAR Method):
1. **Situation**: Set the context
2. **Task**: Explain your responsibility
3. **Action**: Describe what you did
4. **Result**: Share the outcome (with numbers!)

## 🎯 Sample Answer Example

**Question**: "Tell me about a challenging project you worked on."

**Poor Answer** (Score: 45/100):
"Um, I worked on a project that was hard. It was challenging and I had to work with my team. We finished it eventually."

**Good Answer** (Score: 85/100):
"In my previous role as a software engineer, our team faced a critical performance issue where page load times exceeded 8 seconds, impacting 10,000+ daily users. I took the lead on investigating the root cause, identified inefficient database queries, and implemented caching mechanisms. Within two weeks, we reduced load times by 75% to under 2 seconds, which increased user engagement by 30% and received positive feedback from management."

### Why the Good Answer Scores Higher:
✅ Specific role and context
✅ Quantified problem (8 seconds, 10,000 users)
✅ Clear action taken (investigation, implementation)
✅ Measurable results (75% improvement, 30% engagement)
✅ Professional language
✅ Well-structured narrative

## 🚨 Common Issues & Quick Fixes

### "No module named 'xxx'"
```bash
# Run this:
pip install -r requirements.txt --upgrade
```

### "Microphone not detected"
1. Check System Settings → Privacy → Microphone
2. Allow Python/Terminal to access microphone
3. Try unplugging and replugging microphone

### "Camera not found"
1. Check System Settings → Privacy → Camera
2. Close other apps using camera (Zoom, Teams, etc.)
3. Try different camera_index in config (0, 1, or 2)

### "API key not working"
1. Check for extra spaces in .env file
2. Verify key is active on API provider website
3. Ensure you have credits/quota available

### "Speech not recognized"
1. Speak louder and clearer
2. Reduce background noise
3. Check internet connection
4. Try speaking in shorter sentences

## 📊 Understanding Your Scores

| Component | Weight | What It Measures |
|-----------|--------|------------------|
| **Content** | 40% | Examples, specifics, achievements |
| **Clarity** | 25% | Clear communication, no fillers |
| **Confidence** | 20% | Positive tone, conviction |
| **Visual** | 15% | Eye contact, expressions, posture |

### Score Interpretation:
- **85-100**: Excellent - Ready for real interviews!
- **70-84**: Good - Minor improvements needed
- **50-69**: Average - Practice specific areas
- **Below 50**: Keep practicing - Review feedback carefully

## 🎓 Practice Exercises

### Exercise 1: The 30-Second Intro
Practice answering "Tell me about yourself" in exactly 30 seconds.
Focus on: Current role → Key skills → Career goal

### Exercise 2: STAR Stories
Prepare 5 STAR stories covering:
1. Problem-solving
2. Teamwork
3. Leadership
4. Conflict resolution
5. Technical challenge

### Exercise 3: Eye Contact
Practice looking at camera while speaking for 1 minute.
Record yourself and watch back.

### Exercise 4: Reduce Fillers
Record yourself answering questions.
Count "um", "uh", "like" - aim for zero!

## 📅 Interview Preparation Checklist

**1 Week Before:**
- [ ] Research company and role
- [ ] Prepare STAR stories
- [ ] List your achievements with numbers
- [ ] Practice with AI system

**3 Days Before:**
- [ ] Practice common questions
- [ ] Review technical concepts
- [ ] Test equipment (camera, mic)
- [ ] Do mock interview

**1 Day Before:**
- [ ] Review your resume
- [ ] Prepare questions to ask
- [ ] Plan your outfit
- [ ] Get good rest

**Day Of:**
- [ ] Test technology 1 hour before
- [ ] Review key points
- [ ] Stay hydrated
- [ ] Arrive early (or log in early)

## 💡 Pro Tips

1. **The 2-Minute Rule**: Keep answers under 2 minutes
2. **Numbers Win**: Always quantify results when possible
3. **Smile**: Even on audio calls - it changes your tone
4. **Pause is OK**: Brief pauses show thoughtfulness
5. **End Strong**: Finish answers confidently, don't trail off

## 🎯 Next Steps After Your Mock Interview

1. **Review PDF Report** - Read all sections carefully
2. **Watch Score Trends** - Which areas need most work?
3. **Address Weak Points** - Practice those specific areas
4. **Repeat Weekly** - Track improvement over time
5. **Real Interview** - You're ready when scoring 75+!

## 📚 Additional Resources

**Interview Skills:**
- Glassdoor Interview Questions
- Cracking the Coding Interview (book)
- YouTube: Mock interview channels

**Technical Practice:**
- LeetCode (coding)
- System Design Primer
- Behavioral Interview Guide

**Communication:**
- Toastmasters (public speaking)
- Dale Carnegie courses
- Record & review yourself

## ❓ FAQ

**Q: How many practice interviews should I do?**
A: At least 3-5 before your real interview. More for important roles.

**Q: Can I pause during the interview?**
A: No, it runs continuously. But you can take brief pauses between thoughts.

**Q: Do I need a job description?**
A: Recommended but not required. System generates generic questions if omitted.

**Q: Is my data saved?**
A: Only the final PDF report is saved. Video/audio are processed in real-time only.

**Q: Can I review questions before starting?**
A: Questions are shown after generation but before interview starts.

**Q: What if I don't finish an answer?**
A: That's OK! Just like a real interview, you'll move to next question.

---

## 🚀 Ready to Start?

Run this command:
```bash
python interview_system.py
```

**Remember**: This is PRACTICE. Don't stress about perfect scores.
Focus on IMPROVEMENT with each attempt!

Good luck! 🎯✨