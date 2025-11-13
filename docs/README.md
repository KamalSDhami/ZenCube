# ZenCube Team Documentation - README

## 📚 Documentation Index

Welcome to the ZenCube project documentation! This folder contains comprehensive guides for understanding and presenting the project.

---

## 🗂️ Document Structure

### 1. **PROJECT_OVERVIEW.md** - Start Here!
📖 **Complete project documentation**
- High-level architecture
- System flow diagrams
- Technology stack
- File structure and purpose
- Security model
- Performance considerations

**Read this first to understand the big picture!**

---

### 2. **ROLE_1_CORE_SANDBOX.md** - C Developer
🔧 **Core sandbox implementation (sandbox.c)**
- System calls deep dive (fork, exec, wait, setrlimit)
- Process lifecycle management
- Resource limit enforcement
- Signal handling
- Kernel-level interactions

**For the person explaining the C code and system programming**

**Key Topics:**
- How fork() creates processes
- How setrlimit() enforces limits
- How execvp() executes programs
- Process states and signals
- Memory management

---

### 3. **ROLE_2_GUI_FRONTEND.md** - GUI Developer  
🎨 **User interface (zencube_modern_gui.py)**
- PySide6 framework
- Custom widget development
- Modern UI design principles
- Responsive layout (FlowLayout)
- Styling and themes
- Threading for responsiveness

**For the person explaining the GUI and user experience**

**Key Topics:**
- Why PySide6 over Tkinter
- Custom component architecture
- FlowLayout for responsive design
- QThread for async execution
- Signal-slot mechanism
- Color-coded output

---

### 4. **ROLE_3_INTEGRATION.md** - Integration Engineer
🔗 **Python-C bridge and process management**
- Command building from GUI state
- subprocess.Popen usage
- WSL integration (Windows support)
- Output streaming
- Error handling
- State management

**For the person explaining how components connect**

**Key Topics:**
- build_command() method
- CommandExecutor threading
- WSL path conversion
- Process execution flow
- Output capture and display
- Cross-platform compatibility

---

### 5. **ROLE_4_TESTING.md** - QA Engineer
🧪 **Testing, validation, and security**
- Test program development
- Adversarial testing approach
- Security validation
- Attack simulation
- Test results documentation

**For the person explaining testing and quality assurance**

**Key Topics:**
- infinite_loop.c (CPU test)
- memory_hog.c (Memory test)
- fork_bomb.c (Process test)
- file_size_test.c (File size test)
- Why tests are safe despite simulating attacks
- Test result validation

---

### 6. **QA_PREPARATION.md** - Question & Answer Guide
💬 **Comprehensive Q&A for mentor session**
- Anticipated questions with detailed answers
- Technical deep dives
- System design questions
- Security questions
- Comparison questions (Docker, ulimit, etc.)
- Presentation strategies
- Demo flow
- Handling difficult questions

**Study this before your presentation!**

---

### 7. **MONITORING_DASHBOARD.md** - Monitoring & Metrics Panel
📈 **Native dashboard for Task C**
- Sampling monitor overview
- JSONL artefacts format
- GUI workflow and integration notes
- Testing instructions for the offscreen regression script
- Future enhancements roadmap

---

## 🎯 How to Use This Documentation

### For Individual Study:

**Day 1-2: Foundation**
1. Read `PROJECT_OVERVIEW.md` completely
2. Read your role-specific document (ROLE_X.md)
3. Note down concepts you don't understand

**Day 3: Deep Dive**
4. Re-read your role document slowly
5. Follow along with the actual code
6. Try to explain concepts out loud to yourself

**Day 4: Integration**
7. Skim through OTHER role documents
8. Understand how your part fits into the whole
9. Review `QA_PREPARATION.md`

**Day 5: Practice**
10. Practice explaining your role
11. Practice running demos
12. Review Q&A answers

### For Team Preparation:

**Team Meeting 1: Overview**
- Everyone reads `PROJECT_OVERVIEW.md`
- Discuss high-level architecture together
- Assign roles officially

**Team Meeting 2: Deep Dive**
- Each person presents their role (15 min each)
- Others ask questions
- Identify gaps in understanding

**Team Meeting 3: Integration**
- Walk through complete execution flow together
- Each person explains their part in sequence
- Practice handoffs between roles

**Team Meeting 4: Q&A Practice**
- Take turns asking questions from QA_PREPARATION.md
- Practice answering under pressure
- Give each other feedback

**Team Meeting 5: Full Rehearsal**
- Complete presentation run-through
- Time yourselves
- Identify weak points
- Polish transitions

---

## 👥 Role Assignment Guide

### How to Assign Roles:

**Role 1: Core Sandbox (C Developer)**
- **Best for**: Strong in C programming, understands operating systems
- **Needs to know**: System calls, process management, Linux internals
- **Personality**: Detail-oriented, comfortable with low-level concepts
- **Demo**: Live code walkthrough of sandbox.c

**Role 2: GUI Frontend**
- **Best for**: Python developer, interested in UI/UX
- **Needs to know**: PySide6/Qt, threading, design principles
- **Personality**: Visual thinker, enjoys user experience design
- **Demo**: GUI demonstration, show responsive features

**Role 3: Integration**
- **Best for**: Full-stack thinking, understands both C and Python
- **Needs to know**: Process communication, cross-platform issues
- **Personality**: Big-picture thinker, connector
- **Demo**: Show how clicking Execute leads to sandbox execution

**Role 4: Testing/QA**
- **Best for**: Security-minded, detail-oriented, thorough
- **Needs to know**: Security testing, attack vectors, validation
- **Personality**: Skeptical, thinks about edge cases
- **Demo**: Run test suite, explain adversarial testing

---

## 📊 Presentation Flow Suggestion

### 20-Minute Presentation Structure:

**1. Introduction (2 min)** - Role 3 (Integration)
- What is ZenCube?
- Why does it matter?
- Real-world applications
- Team introduction

**2. Architecture Overview (3 min)** - Role 1 (Core)
- Show architecture diagram
- Explain layers (GUI → Integration → Sandbox → Kernel)
- Component responsibilities

**3. Core Sandbox Demo (5 min)** - Role 1 (Core)
- Open sandbox.c
- Walk through main() function
- Explain fork, setrlimit, exec, wait
- Run CPU limit test live

**4. GUI Demonstration (4 min)** - Role 2 (GUI)
- Open GUI application
- Explain interface sections
- Run quick command
- Show responsive design
- Highlight threading (GUI stays responsive)

**5. Integration & Flow (3 min)** - Role 3 (Integration)
- Explain command building
- Show build_command() code
- Discuss WSL support
- Trace execution from button click to output

**6. Testing & Validation (3 min)** - Role 4 (Testing)
- Explain adversarial testing approach
- Show test programs (infinite_loop, memory_hog, fork_bomb)
- Run one test live
- Discuss security implications

**7. Q&A (Remaining time)** - All roles
- Be prepared for deep technical questions
- Support each other
- Don't be afraid to say "I don't know, but..."

---

## 🔑 Key Concepts Everyone Should Know

### Essential Understanding:

**1. What ZenCube Does**
```
Executes programs with enforced resource limits
(CPU time, memory, processes, file size)
```

**2. Why It's Needed**
```
Prevents malicious/buggy code from crashing systems
Real-world use: Online judges, CI/CD, security research
```

**3. How It Works (High Level)**
```
GUI → Python subprocess → C sandbox → Linux kernel
Kernel enforces limits at hardware level
```

**4. Key Technologies**
```
C: Low-level system calls (fork, exec, setrlimit)
Python: GUI (PySide6) and integration
Linux: Kernel-level resource enforcement
```

**5. Security Model**
```
What we protect: Resource exhaustion
What we don't: Filesystem, network (honest about limitations)
```

### Quick Facts:

| Metric | Value |
|--------|-------|
| **Lines of Code** | ~1500 (C + Python) |
| **Development Time** | ~3 weeks |
| **Team Size** | 4 developers |
| **Test Programs** | 4 attack simulations |
| **Supported Limits** | CPU, Memory, Processes, File Size |
| **Platform** | Linux, Windows (via WSL) |

---

## 📝 Cheat Sheets

### System Calls Quick Reference

```c
fork()      // Create child process
            // Returns: 0 in child, PID in parent

setrlimit() // Set resource limits
            // Types: RLIMIT_CPU, RLIMIT_AS, RLIMIT_NPROC, RLIMIT_FSIZE

execvp()    // Replace process with new program
            // Never returns on success

waitpid()   // Wait for child to finish
            // Returns: child's exit status
```

### Signals Quick Reference

```
SIGXCPU (24) - CPU time limit exceeded
SIGKILL (9)  - Force kill (often memory limit)
SIGXFSZ (25) - File size limit exceeded
SIGTERM (15) - Termination request (can catch)
```

### Python Threading Quick Reference

```python
# Create thread
executor = CommandExecutor(command)

# Connect signals
executor.output_received.connect(handler)
executor.finished_signal.connect(handler)

# Start execution
executor.start()  # Non-blocking!
```

---

## 🚀 Pre-Presentation Checklist

### Technical Setup:
- [ ] All code compiles without errors
- [ ] GUI launches successfully
- [ ] All test programs compiled
- [ ] Test suite runs successfully
- [ ] WSL configured (if on Windows)

### Knowledge Check:
- [ ] Can explain project in 30 seconds (elevator pitch)
- [ ] Can explain project in 5 minutes (overview)
- [ ] Understand your role deeply
- [ ] Understand other roles at high level
- [ ] Read QA_PREPARATION.md completely

### Demo Preparation:
- [ ] Practice running demos
- [ ] Know expected output for each test
- [ ] Have code editors ready (with right files open)
- [ ] Know line numbers of key functions
- [ ] Prepared for "show me the code" requests

### Mental Preparation:
- [ ] Well-rested
- [ ] Confident about what you know
- [ ] Honest about what you don't know
- [ ] Ready to learn from mentor's questions
- [ ] Excited to show your work!

---

## 💡 Tips for Success

### During Presentation:

**DO:**
- ✅ Start with a compelling example (fork bomb demo!)
- ✅ Use analogies (sandbox = "safety container")
- ✅ Show enthusiasm - you built something cool!
- ✅ Admit when you don't know something
- ✅ Support your teammates
- ✅ Ask for clarification if question is unclear

**DON'T:**
- ❌ Memorize and recite - understand and explain
- ❌ Oversell capabilities - be honest about limitations
- ❌ Panic when interrupted - it shows engagement
- ❌ Blame teammates if something doesn't work
- ❌ Make up answers - say "I don't know" instead

### Handling Questions:

**"I don't know":**
```
"That's a great question. I'm not sure about [X], 
 but I know [Y] and here's how they might relate..."
```

**"Let me show you":**
```
Better to demo than explain!
Open the code, run the test, show the output
```

**"Can you rephrase that?":**
```
If question is unclear, ask for clarification:
"Just to make sure I understand, are you asking about [X]?"
```

---

## 📞 Team Communication

### Before Presentation:
- Share this document with everyone
- Schedule team practice sessions
- Support each other in learning
- Quiz each other with questions

### During Presentation:
- Make eye contact with teammates
- Hand off smoothly between sections
- Jump in to support if someone struggles
- "Let me add to what [teammate] said..."

### After Presentation:
- Debrief together
- What went well?
- What could improve?
- Celebrate your success!

---

## 🎓 Learning Outcomes

By presenting ZenCube, you'll demonstrate understanding of:

**System Programming:**
- Process management (fork, exec, wait)
- Resource limits and kernel interfaces
- Signal handling
- Memory management

**Software Engineering:**
- Multi-layer architecture
- Component integration
- Error handling
- Testing strategies

**Security:**
- Sandboxing techniques
- Attack vectors (fork bombs, memory exhaustion)
- Defense mechanisms
- Honest evaluation of limitations

**GUI Development:**
- Modern UI frameworks (Qt/PySide6)
- Responsive design
- Threading and async operations
- User experience principles

---

## 📚 Additional Resources

### If You Want to Go Deeper:

**Books:**
- "Advanced Programming in the UNIX Environment" by Stevens
- "The Linux Programming Interface" by Kerrisk

**Man Pages:**
```bash
man fork
man exec
man setrlimit
man wait
man signal
```

**Online:**
- Linux System Call Reference: https://man7.org
- Qt Documentation: https://doc.qt.io
- Python subprocess: https://docs.python.org/3/library/subprocess.html

---

## 🏆 Final Words

You've built a legitimate systems programming project that demonstrates real CS concepts:

- ✅ Process management
- ✅ Operating system interfaces
- ✅ Security considerations
- ✅ User interface design
- ✅ Integration engineering
- ✅ Quality assurance

**This is impressive work!** 

Be confident. Be honest. Be ready to learn from your mentor's questions.

**You've got this! 🚀**

---

## 📋 Quick Start Checklist

**30 Minutes Before Presentation:**
1. [ ] Read your role document one more time
2. [ ] Review key Q&A topics
3. [ ] Test your demos
4. [ ] Take a deep breath

**During Presentation:**
1. [ ] Introduce yourself and your role
2. [ ] Speak clearly and confidently
3. [ ] Show, don't just tell (live demos!)
4. [ ] Support your teammates

**After Presentation:**
1. [ ] Thank the mentor for their time
2. [ ] Note any questions you couldn't answer
3. [ ] Research those topics
4. [ ] Celebrate with your team!

---

**Good luck! You've prepared well. Now go show what you've learned!** 🎉
