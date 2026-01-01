# 📖 Task Follow-up System - Employee Training Guide

## 🎯 Overview

The **Task Follow-up System** automatically tracks action items from meetings and sends reminders. This guide explains how to respond to reminder emails so the system can automatically update task status.

---

## 📧 How You'll Receive Reminders

### **Reminder Email Format:**

```
Subject: ⏰ Pending Action Items – Reminder

Dear Sarika,

This is a gentle reminder for the following pending action items:

• Task ID: MOM-20251231-001-T16
  Task: Noted the new portal for the UK. What is the status?
  Source: MOM-20251231-001

• Task ID: MOM-20251231-001-T18
  Task: More focus is required on automation and team utilisation.
  Source: MOM-20251231-001

Kindly let me know once completed.

Best regards,
Task Follow-up Team
```

---

## ✅ How to Reply (Auto-Processing)

### **Method 1: Simple Format (Recommended)**

**Just reply with Task ID and status:**

```
Dear Sir,

MOM-20251231-001-T16: COMPLETED
MOM-20251231-001-T18: COMPLETED
MOM-20251231-001-T19: Pending - need more clarification

Regards,
Sarika
```

**What Happens:**
- ✅ System automatically marks T16 and T18 as COMPLETED
- 🔄 Keeps T19 as pending
- 📧 Sends you acknowledgment with summary

---

### **Method 2: Detailed Format**

**For more context:**

```
Dear Sir,

Task ID: MOM-20251231-001-T16
Status: COMPLETED
Notes: Portal access received and tested successfully.

Task ID: MOM-20251231-001-T18
Status: COMPLETED
Notes: PFA team ratings for December 2025.

Task ID: MOM-20251231-001-T19
Status: Pending
Notes: Awaiting threshold limits clarification from finance.

Regards,
Sarika
```

**What Happens:**
- ✅ System marks completed tasks
- 📝 Saves your notes for reference
- 📊 Tracks performance (on-time vs late)
- 📧 Sends acknowledgment

---

### **Method 3: Mixed Format (Flexible)**

**You can combine both:**

```
Dear Sir,

Quick updates:

MOM-20251231-001-T16: COMPLETED - Portal working fine
MOM-20251231-001-T18: COMPLETED
MOM-20251231-001-T19: Still pending, need info from Ajay

Detailed response for T19:
I've reached out to Ajay for the threshold data. 
Expected by end of week.

Regards,
Sarika
```

---

## 🤖 System's Automatic Response

**After you reply, you'll receive:**

```
Subject: Re: ⏰ Pending Action Items – Reminder

Dear Sarika,

Thank you for the update. We acknowledge the following:

✅ COMPLETED TASKS:
• MOM-20251231-001-T16: Noted the new portal for the UK
• MOM-20251231-001-T18: Automation and team utilisation

🔄 PENDING TASKS:
• MOM-20251231-001-T19: E-invoicing information
  Note: Awaiting threshold limits clarification

Please work on the pending tasks and let us know once completed.

Best regards,
Task Follow-up Team
```

---

## 🎯 Magic Keywords

### **To Mark as COMPLETED:**

Use any of these keywords:
- `COMPLETED`
- `COMPLETE`
- `DONE`
- `FINISHED`
- `CLOSED`
- `RESOLVED`

**Example:**
```
MOM-001-T16: COMPLETED
MOM-001-T17: DONE
MOM-001-T18: FINISHED
```

### **To Keep as PENDING:**

Use any of these:
- `PENDING`
- `IN PROGRESS`
- `WORKING ON`
- `AWAITING`
- `NEED`
- `WAITING FOR`

**Example:**
```
MOM-001-T19: PENDING - need approval
MOM-001-T20: IN PROGRESS
MOM-001-T21: AWAITING data from IT
```

---

## ✅ DO's

1. ✅ **Reply to the same email thread** (keeps conversation linked)
2. ✅ **Include the Task ID** (e.g., MOM-001-T16)
3. ✅ **Use clear keywords** (COMPLETED, PENDING)
4. ✅ **Add brief notes** if helpful
5. ✅ **Reply promptly** (helps with tracking)

---

## ❌ DON'Ts

1. ❌ **Don't create new email thread** (reply to reminder email)
2. ❌ **Don't delete Task IDs** (system needs them)
3. ❌ **Don't use vague terms** like "okay" or "noted"
4. ❌ **Don't forget to mention pending tasks** 
5. ❌ **Don't reply without Task ID reference**

---

## 📊 What Happens Behind the Scenes

### **When You Reply:**

1. 🤖 **System reads your email**
2. 🔍 **Finds Task IDs and keywords**
3. ✅ **Auto-completes tasks with "COMPLETED"**
4. 📝 **Saves notes and status updates**
5. 📊 **Tracks performance** (on-time vs delayed)
6. 📧 **Sends acknowledgment** with summary
7. 📈 **Updates dashboard** (for Praveen to review)

### **If All Tasks Completed:**

```
Dear Sarika,

Excellent work! All action items have been completed:

✅ MOM-20251231-001-T16: UK portal status
✅ MOM-20251231-001-T18: Automation & ratings
✅ MOM-20251231-001-T19: E-invoicing information

No further action required.

Best regards,
Task Follow-up Team
```

---

## 🎯 Quick Reference Card

### **Template for Your Reply:**

```
Dear Sir,

[Task ID]: [COMPLETED/PENDING] - [Optional notes]
[Task ID]: [COMPLETED/PENDING] - [Optional notes]
[Task ID]: [COMPLETED/PENDING] - [Optional notes]

Regards,
[Your Name]
```

### **Example:**

```
Dear Sir,

MOM-20251231-001-T16: COMPLETED
MOM-20251231-001-T18: COMPLETED - PFA document
MOM-20251231-001-T19: PENDING - need clarification

Regards,
Sarika
```

---

## ❓ FAQ

### **Q: What if I partially complete a task?**
**A:** Mark it as PENDING and add notes:
```
MOM-001-T16: PENDING - 80% complete, final review pending
```

### **Q: What if I need more time?**
**A:** Mark as PENDING with reason:
```
MOM-001-T17: PENDING - awaiting client response
```

### **Q: Can I reply with detailed explanations?**
**A:** Yes! System extracts Task ID and status, ignores rest:
```
MOM-001-T18: COMPLETED

Detailed notes:
I've completed the full analysis and attached the report.
Key findings include... [your detailed response]
```

### **Q: What if I forget Task ID?**
**A:** System tries to match based on context, but it's better to include Task ID for accuracy.

### **Q: Will I get confirmation?**
**A:** Yes! You'll receive an acknowledgment email with summary within minutes.

---

## 📞 Support

**Questions?** Contact Praveen Kumar
- Email: praveen.chaudhary@koenig-solutions.com

---

## 🎓 Training Summary

| You Do | System Does |
|--------|-------------|
| Reply with "COMPLETED" | ✅ Auto-closes task |
| Reply with "PENDING" | 🔄 Keeps tracking |
| Add notes | 📝 Saves for reference |
| Reply promptly | 📊 Shows good performance |
| Complete on time | ⭐ Records "On Time" rating |

---

**Remember:** The more consistent you are with the format, the better the automation works! 🚀

---

**Last Updated:** January 2, 2026
**Version:** 1.0
