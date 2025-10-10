import React, { useEffect, useRef } from 'react';

const MorningBriefLanding = () => {
  const observerRef = useRef();

  useEffect(() => {
    // Intersection Observer for animations
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    observerRef.current = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-fade-in-up');
        }
      });
    }, observerOptions);

    // Observe all fade-in elements
    document.querySelectorAll('.fade-in').forEach(el => {
      observerRef.current.observe(el);
    });

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleCTAClick = (type) => {
    if (type === 'primary') {
      alert('🚀 Redirecting to Telegram bot setup...\n\nIn a real implementation, this would:\n1. Open Telegram\n2. Start a conversation with @MorningBriefBot\n3. Guide user through category selection');
    } else if (type === 'secondary') {
      scrollToSection('preview');
    } else if (type === 'waitlist') {
      alert('📝 Thank you for your interest!\n\nYou\'ll be notified when Pro features are available.');
    }
  };

  return (
    <div className="bg-white text-slate-800 font-inter">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="text-2xl font-bold text-slate-900">
              📰 MorningBrief
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <button onClick={() => scrollToSection('how-it-works')} className="text-slate-600 hover:text-slate-900 transition-colors">
                How it works
              </button>
              <button onClick={() => scrollToSection('benefits')} className="text-slate-600 hover:text-slate-900 transition-colors">
                Benefits
              </button>
              <button onClick={() => scrollToSection('preview')} className="text-slate-600 hover:text-slate-900 transition-colors">
                Preview
              </button>
              <button onClick={() => scrollToSection('pricing')} className="text-slate-600 hover:text-slate-900 transition-colors">
                Pricing
              </button>
              <button 
                onClick={() => handleCTAClick('primary')}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-50 to-slate-200 py-20 lg:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="fade-in">
              <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight mb-6">
                Get your daily brief before your coffee's ready
              </h1>
              <p className="text-xl text-slate-600 mb-8 leading-relaxed">
                Stop scrolling through endless feeds. Receive a concise, curated summary of what matters — in just 2 minutes, every morning.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={() => handleCTAClick('primary')}
                  className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:shadow-lg transition-all transform hover:scale-105"
                >
                  📱 Get My Morning Brief
                </button>
                <button 
                  onClick={() => handleCTAClick('secondary')}
                  className="bg-white text-slate-700 px-8 py-4 rounded-xl font-semibold text-lg border border-slate-300 hover:bg-slate-50 transition-colors"
                >
                  👀 See a Sample Brief
                </button>
              </div>
            </div>
            <div className="fade-in">
              {/* Product Mockup */}
              <div className="relative">
                <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-md mx-auto">
                  <div className="flex items-center mb-6">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                      MB
                    </div>
                    <div className="ml-3">
                      <div className="font-semibold text-slate-900">MorningBrief</div>
                      <div className="text-sm text-slate-500">Today • 7:00 AM</div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    {[
                      { icon: '🚀', category: 'Tech', content: 'Breakthrough in quantum computing shows 1000x speed improvement...' },
                      { icon: '💼', category: 'Business', content: 'Major merger announced between two Fortune 500 companies...' },
                      { icon: '🌍', category: 'World', content: 'Climate summit reaches historic agreement on carbon reduction...' }
                    ].map((item, index) => (
                      <div key={index} className="bg-slate-50 rounded-lg p-4">
                        <div className="font-medium text-slate-900 mb-2">{item.icon} {item.category}</div>
                        <div className="text-sm text-slate-600">{item.content}</div>
                      </div>
                    ))}
                  </div>
                  <div className="mt-6 text-center">
                    <div className="text-sm text-slate-500">📖 2 min read • 12 stories</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">How it works</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Three simple steps to transform your morning routine
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: '⚙️', title: '1. Choose categories', description: 'Select the topics that matter to you: tech, business, world news, and more.' },
              { icon: '🤖', title: '2. Smart curation', description: 'Our system scans hundreds of sources and picks the most important stories for you.' },
              { icon: '📱', title: '3. Receive your brief', description: 'Get a concise summary delivered to your phone every morning at 7 AM.' }
            ].map((step, index) => (
              <div key={index} className="text-center fade-in">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <span className="text-2xl">{step.icon}</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-4">{step.title}</h3>
                <p className="text-slate-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="py-20 bg-gradient-to-br from-slate-50 to-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Why professionals choose MorningBrief</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Start your day smarter, not overwhelmed
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: '⏰', bgColor: 'bg-green-100', title: 'Save time', description: 'Get key info in just 2 minutes instead of scrolling for hours through social feeds.' },
              { icon: '🎯', bgColor: 'bg-blue-100', title: 'Stay informed', description: 'Curated from top sources ensures you never miss what actually matters.' },
              { icon: '🚀', bgColor: 'bg-purple-100', title: 'Boost productivity', description: 'Start your day smarter with context and insights that help you make better decisions.' }
            ].map((benefit, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1 fade-in">
                <div className={`w-12 h-12 ${benefit.bgColor} rounded-lg flex items-center justify-center mb-6`}>
                  <span className="text-2xl">{benefit.icon}</span>
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-4">{benefit.title}</h3>
                <p className="text-slate-600">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Preview Section */}
      <section id="preview" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">See it in action</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Here's what your morning brief looks like
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <div className="bg-slate-900 rounded-2xl p-8 shadow-2xl">
              <div className="bg-white rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                      MB
                    </div>
                    <div className="ml-3">
                      <div className="font-semibold text-slate-900">Your Morning Brief</div>
                      <div className="text-sm text-slate-500">Tuesday, March 12 • 7:00 AM</div>
                    </div>
                  </div>
                  <div className="text-sm text-slate-500">📖 2 min read</div>
                </div>
                
                <div className="space-y-6">
                  {[
                    { color: 'border-blue-500', icon: '🚀', category: 'Technology', title: 'OpenAI announces GPT-5 with breakthrough reasoning capabilities', content: 'The new model shows significant improvements in complex problem-solving and mathematical reasoning, potentially revolutionizing AI applications in science and engineering.' },
                    { color: 'border-green-500', icon: '💼', category: 'Business', title: 'Tesla reports record quarterly deliveries', content: 'Electric vehicle giant delivered 500,000 cars in Q1, beating analyst expectations and driving stock price up 8% in pre-market trading.' },
                    { color: 'border-orange-500', icon: '🌍', category: 'World', title: 'Global climate summit reaches historic agreement', content: '195 countries commit to new carbon reduction targets, with binding commitments to achieve net-zero emissions by 2050.' }
                  ].map((article, index) => (
                    <div key={index} className={`border-l-4 ${article.color} pl-4`}>
                      <div className="flex items-center mb-2">
                        <span className="text-lg mr-2">{article.icon}</span>
                        <span className="font-semibold text-slate-900">{article.category}</span>
                      </div>
                      <h3 className="font-semibold text-slate-900 mb-2">{article.title}</h3>
                      <p className="text-slate-600 text-sm">{article.content}</p>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 pt-6 border-t border-slate-200 text-center">
                  <p className="text-sm text-slate-500">📊 12 stories from 8 categories • Powered by AI</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Trusted by professionals</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              See what busy professionals are saying
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'Sarah Johnson', role: 'Product Manager, Tech Startup', avatar: 'SJ', bgColor: 'bg-blue-500', quote: 'Finally, a news source that respects my time. I get everything I need to know in 2 minutes.' },
              { name: 'Michael Chen', role: 'Investment Analyst', avatar: 'MC', bgColor: 'bg-green-500', quote: 'The AI curation is spot-on. I never miss important industry news anymore.' },
              { name: 'Amanda Rodriguez', role: 'CEO, Marketing Agency', avatar: 'AR', bgColor: 'bg-purple-500', quote: 'Perfect for busy executives. I start every day informed and confident.' }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg fade-in">
                <div className="mb-6">
                  <div className="text-yellow-400 text-xl mb-4">⭐⭐⭐⭐⭐</div>
                  <p className="text-slate-600 italic">"{testimonial.quote}"</p>
                </div>
                <div className="flex items-center">
                  <div className={`w-10 h-10 ${testimonial.bgColor} rounded-full flex items-center justify-center text-white font-semibold text-sm`}>
                    {testimonial.avatar}
                  </div>
                  <div className="ml-3">
                    <div className="font-semibold text-slate-900">{testimonial.name}</div>
                    <div className="text-sm text-slate-500">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">Simple, transparent pricing</h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Start free, upgrade when you're ready
            </p>
          </div>
          <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
            <div className="bg-white border-2 border-slate-200 rounded-2xl p-8 text-center">
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Free</h3>
                <p className="text-slate-600">Perfect to get started</p>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-slate-900">$0</span>
                  <span className="text-slate-500">/month</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8 text-left">
                {[
                  'Daily briefings on Telegram',
                  '5 news categories',
                  'Curated content',
                  '2-minute read time'
                ].map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <span className="text-green-500 mr-3">✓</span>
                    <span className="text-slate-600">{feature}</span>
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleCTAClick('primary')}
                className="w-full bg-slate-100 text-slate-700 py-3 rounded-xl font-semibold hover:bg-slate-200 transition-colors"
              >
                Start Free on Telegram
              </button>
            </div>
            
            <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-8 text-center relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold">Coming Soon</span>
              </div>
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-slate-900 mb-2">Pro</h3>
                <p className="text-slate-600">For power users</p>
                <div className="mt-4">
                  <span className="text-4xl font-bold text-slate-900">$9</span>
                  <span className="text-slate-500">/month</span>
                </div>
              </div>
              <ul className="space-y-4 mb-8 text-left">
                {[
                  'Everything in Free',
                  'Unlimited categories',
                  'Custom delivery times',
                  'Email & SMS delivery',
                  'Priority support'
                ].map((feature, index) => (
                  <li key={index} className="flex items-center">
                    <span className="text-green-500 mr-3">✓</span>
                    <span className="text-slate-600">{feature}</span>
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleCTAClick('waitlist')}
                className="w-full bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors"
              >
                Join Waitlist
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="text-2xl font-bold mb-4">📰 MorningBrief</div>
              <p className="text-slate-400 mb-6 max-w-md">
                Get your daily brief before your coffee's ready. AI-curated news summaries for busy professionals.
              </p>
              <div className="flex space-x-4">
                {[
                  { icon: '🐦', label: 'Twitter' },
                  { icon: '💼', label: 'LinkedIn' },
                  { icon: '📱', label: 'Telegram' }
                ].map((social, index) => (
                  <button key={index} className="text-slate-400 hover:text-white transition-colors">
                    <span className="sr-only">{social.label}</span>
                    {social.icon}
                  </button>
                ))}
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                {['How it works', 'Features', 'Pricing', 'API'].map((item, index) => (
                  <li key={index}>
                    <button className="text-slate-400 hover:text-white transition-colors">{item}</button>
                  </li>
                ))}
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                {['About', 'Contact', 'Privacy', 'Terms'].map((item, index) => (
                  <li key={index}>
                    <button className="text-slate-400 hover:text-white transition-colors">{item}</button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="border-t border-slate-800 mt-12 pt-8 text-center">
            <p className="text-slate-400">
              © 2024 MorningBrief. All rights reserved. Built with ❤️ for busy professionals.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MorningBriefLanding;
