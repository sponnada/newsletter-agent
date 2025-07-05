import asyncio
import json
from newsletter.agent import NewsletterAgent

async def main():
    """Run the newsletter agent"""
    print("🚀 Starting Newsletter Agent...")
    
    try:
        async with NewsletterAgent() as agent:
            newsletter_content = await agent.run()
            print("✅ Newsletter generated successfully!")
            print("\n📰 Preview:")
            print("-" * 50)
            print(newsletter_content[:300] + "...")
            print("-" * 50)
            print("\n📁 Check your folder for the complete newsletter file!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you have created config.json and have internet connection")

if __name__ == "__main__":
    asyncio.run(main())