import React from 'react';

function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 py-8 px-6 mt-12">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <span className="text-sm font-bold text-white">✦</span>
              </div>
              <span className="font-bold text-slate-900">HR Analytics</span>
            </div>
            <p className="text-sm text-slate-600">AI-Powered Employee Attrition Prediction System</p>
          </div>

          {/* Product */}
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-4">Product</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Features</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Pricing</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Documentation</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Updates</a></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-4">Company</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">About</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Blog</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Careers</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Contact</a></li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-sm font-semibold text-slate-900 mb-4">Legal</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Privacy</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Terms</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Security</a></li>
              <li><a href="#" className="text-sm text-slate-600 hover:text-indigo-600 transition-colors">Compliance</a></li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-slate-200 pt-8 flex flex-col sm:flex-row items-center justify-between">
          <p className="text-sm text-slate-600">
            © 2024 HR Analytics. All rights reserved. Enterprise-grade AI predictions.
          </p>
          <div className="flex items-center gap-6 mt-4 sm:mt-0">
            <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M8.29 20v-7.21H5.93V9.62h2.36V7.33c0-2.33 1.43-3.61 3.48-3.61 1 0 1.82.08 2.06.11v2.39h-1.44c-1.13 0-1.35.53-1.35 1.32v1.73h2.69l-.35 2.17h-2.34V20H8.29z" />
              </svg>
            </a>
            <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23 3a10.9 10.9 0 11-3.14 1.53 4.48 4.48 0 00.33-2.82A6.62 6.62 0 0123 3z" />
              </svg>
            </a>
            <a href="#" className="text-slate-500 hover:text-indigo-600 transition-colors">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

export default Footer;
