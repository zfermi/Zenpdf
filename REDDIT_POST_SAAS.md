# Reddit Post for r/SaaS

---

## **Title Options** (Pick one that feels authentic to you):

1. **"Launched my PDF SaaS at $3/month to compete with $12/month giants. Here's my pricing breakdown and why I think I'm not crazy."**

2. **"Built a PDF tool SaaS in 3 months. Pricing it at $3/mo while competitors charge $12. Am I leaving money on the table or playing the long game?"**

3. **"Challenging iLovePDF with aggressive pricing ($3/mo vs their $6-12). Bootstrapped founder seeking brutal feedback."**

---

## **Post Body:**

Hey r/SaaS,

I'm a solo dev who just launched **Best PDF Converter** (bestpdfconverter.online), and I'd love your brutal honest feedback on my pricing strategy. I might be making a huge mistake, but here's my thinking.

### **The Situation**

**Market leaders:**
- iLovePDF: $6-12/month
- Adobe Acrobat: $12.99/month  
- Smallpdf: $9/month
- PDFelement: $9.99/month

**My pricing:**
- Free: 10 operations/day, 50MB files
- Premium: **$3/month** unlimited operations, 100MB files

### **Why $3/month?**

I ran the numbers (bootstrapped, so every dollar matters):

```
Monthly costs per user:
- Railway hosting (PostgreSQL + app): ~$0.40
- PayPal fees (3.5%): ~$0.11
- Storage/bandwidth: ~$0.05
- Total: ~$0.56/user

Profit per user: $2.44/month
```

My logic:
1. **Volume over margin**: I'd rather have 1,000 users at $3 than 100 at $12
2. **Lower barrier to entry**: Easier to convert free → paid at $3
3. **Word of mouth**: "It's only $3" is a powerful referral line
4. **Compete on value, not features**: I can't out-feature Adobe, but I can out-price them

### **What I'm Offering**

**Core features (all tiers):**
- Split PDF (by range, odd/even, specific pages)
- Merge PDF (up to 20 files for premium)
- Compress PDF
- Rotate PDF  
- PDF to Word

**Coming soon:**
- OCR
- Digital signatures
- Batch processing
- API access

**Privacy-first:**
- Files deleted after 1 hour
- No data selling
- Server-side processing (no client-side tracking)
- HTTPS everywhere

### **Tech Stack** (for the curious):

- Backend: Python/Flask + PostgreSQL
- Hosting: Railway (scales automatically)
- Payment: PayPal (lower fees than Stripe for my volume)
- PDF processing: PyPDF2, pdf2docx, Pillow

### **My Concerns**

1. **Am I pricing too low?** Will users think it's low-quality?
2. **Can I scale?** If I get 10k users, hosting costs balloon
3. **Upgrade path?** Should I add a $10 "Pro" tier for businesses?
4. **Sustainability?** Can I maintain this long-term or am I burning out for $2.44/user?

### **Early Traction** (2 weeks live):

- 147 signups (mostly from Product Hunt soft launch)
- 23 premium conversions (15.6% conversion rate)
- $69 MRR (lol, nice)
- Churn: 0% (too early to tell)

### **Questions for r/SaaS:**

1. **Pricing:** Am I leaving money on the table? Should I test $5 or $7?
2. **Positioning:** Should I emphasize "cheap" or "fair pricing"?
3. **Freemium limits:** Is 10 ops/day too generous? Should I drop to 5?
4. **Upsell strategy:** What premium features would justify a $10-15 tier?
5. **Marketing:** Where would YOU promote a PDF tool? (I'm doing SEO + Reddit + LinkedIn)

### **What I'm NOT Asking For**

- "Just raise your prices bro" (I've heard this 100x, looking for nuanced takes)
- Generic advice (I've read all the SaaS playbooks)
- Investors (bootstrapping intentionally)

### **What I AM Asking For**

- Honest feedback on my pricing psychology
- Ideas for premium features worth $10-15/month
- Marketing channels I'm missing
- Red flags you see in my approach

---

### **Proof** (Mods, let me know if you need verification):

- Live site: bestpdfconverter.online
- GitHub: [if you're open-source, link it]
- Analytics screenshot: [optional, shows you're legit]

---

### **Special Offer for r/SaaS**

If you want to test it out, DM me and I'll give you 3 months premium free. I genuinely want feedback from people who build SaaS, not just users.

Also happy to do a teardown/AMA if there's interest.

---

**TL;DR:** Launched PDF SaaS at $3/mo (competitors charge $6-12). Either I'm playing 4D chess or I'm an idiot. Help me figure out which.

---

## **Follow-up Comment Strategy** (Post this as first comment):

**Update:** Wow, didn't expect this response! A few clarifications based on early comments:

**On pricing:**
- Yes, I know I could charge more. My hypothesis is that $3 is the "impulse buy" threshold where people don't even think about it. At $9, they compare features. At $3, they just subscribe.

**On costs:**
- Railway scales automatically. If I hit 10k users, I'd migrate to AWS/GCP with reserved instances. Costs would drop to ~$0.20/user at scale.

**On sustainability:**
- This is a side project (for now). If it hits $2k MRR, I'll go full-time. If not, it's still profitable at current scale.

**On competitors:**
- I'm not trying to kill Adobe. I'm targeting the "I need to split a PDF once a month" user who doesn't want to pay $12/mo.

Keep the feedback coming! This is exactly why I posted here. 🙏

---

## **Alternative: Shorter "Show & Tell" Version**

---

**Title:** "Show r/SaaS: PDF tool with aggressive pricing ($3/mo). 2 weeks in, 15% conversion rate. Feedback welcome."

**Body:**

Built a PDF manipulation SaaS (split, merge, compress, rotate, PDF→Word) and launched 2 weeks ago.

**Pricing:**
- Free: 10 ops/day
- Premium: $3/month unlimited

**Why $3?** Competitors charge $6-12. I'm betting on volume over margin.

**Early results:**
- 147 signups
- 23 paid ($69 MRR)
- 15.6% free→paid conversion

**Tech:** Python/Flask, Railway, PostgreSQL, PayPal

**Questions:**
1. Too cheap? (costs me $0.56/user)
2. What premium features justify $10-15/mo?
3. Marketing channels for PDF tools?

**Link:** bestpdfconverter.online

Honest feedback appreciated. Roast me if needed. 🔥

---

## **Engagement Tips:**

### **DO:**
✅ Respond to EVERY comment within first 2 hours
✅ Be humble and receptive to criticism  
✅ Share actual numbers (Redditors love data)
✅ Admit uncertainties ("I don't know if this will work")
✅ Offer free access to commenters
✅ Post during peak hours (9-11 AM EST, Tuesday-Thursday)

### **DON'T:**
❌ Be overly promotional
❌ Argue with critics (ask clarifying questions instead)
❌ Ignore negative feedback
❌ Use marketing speak ("revolutionary," "game-changing")
❌ Post and ghost (engagement is key)
❌ Cross-post to multiple subreddits immediately (looks spammy)

---

## **Subreddit-Specific Notes:**

### **r/SaaS** (Your target):
- **Vibe:** Founders helping founders, data-driven, skeptical of hype
- **Best flair:** "Show" or "Feedback"
- **Tone:** Humble, data-focused, asking for help
- **Length:** Medium (500-800 words) – they like details

### **Other relevant subreddits** (post AFTER r/SaaS, space them out):

**r/Entrepreneur** (wait 3-4 days):
- More general audience
- Focus on the "challenging giants" narrative
- Shorter, more inspirational tone

**r/smallbusiness** (wait 1 week):
- Target users, not founders
- Focus on affordability and ease of use
- Include use cases (invoices, contracts, etc.)

**r/productivity** (wait 2 weeks):
- User-focused, not technical
- "How I streamlined my PDF workflow"
- Soft promotion, mostly value

**r/SideProject** (wait 1 month):
- Show the journey, not just the product
- Technical details welcome
- More casual tone

---

## **Response Templates** (for common comments):

### **"You should charge more"**
"I appreciate that! My thinking is $3 hits the impulse-buy threshold. At $9, people compare features and I lose to Adobe. At $3, it's a no-brainer. But I'm open to testing higher prices once I have more data. What price point would YOU pay for unlimited PDF operations?"

### **"How will you compete with free tools?"**
"Great question. Free tools either: 1) Sell your data, 2) Have terrible UX, or 3) Limit you to 2 files/day. I'm betting there's a market for 'cheap but good' between 'free but sketchy' and 'expensive but enterprise.' Time will tell if I'm right!"

### **"What's your moat?"**
"Honestly? Not much yet. My moat is speed and pricing. I can ship features faster than Adobe and price lower than everyone. Long-term, I'm building API access and integrations (Zapier, Make, etc.) that create lock-in. But you're right to call this out – it's a risk."

### **"This will never work"**
"You might be right! That's why I'm here. What specifically makes you think it won't work? Is it the pricing, the market, the tech, or something else? Genuinely curious."

---

**Good luck! 🚀 Remember: Reddit rewards authenticity and punishes BS. Be real, be helpful, and engage genuinely.**
