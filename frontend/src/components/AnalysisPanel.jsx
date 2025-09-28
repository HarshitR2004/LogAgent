import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Brain, CheckCircle, AlertCircle } from 'lucide-react';

const AnalysisPanel = ({ analysisData, loading }) => {
  const formatAnalysisContent = (analysis) => {
    if (!analysis) return null;
    
    if (typeof analysis === 'string') {
      // Parse and format the analysis text properly
      let formattedText = analysis;
      
      // Clean up any markdown artifacts and code blocks
      formattedText = formattedText.replace(/```\w*\n?/g, '');
      
      // Format timestamps FIRST as inline code (before other replacements)
      formattedText = formattedText.replace(/(\d{1,2}:\d{2}:\d{2})/g, '`$1`');
      
      // Format percentages and metrics as bold
      formattedText = formattedText.replace(/(\d+\.?\d*%)/g, '**$1**');
      formattedText = formattedText.replace(/(\d+\.?\d*\s*GB|\d+\.?\d*\s*MB|\d+\.?\d*\s*KB)/g, '**$1**');
      
      // Convert other backticks to bold (but preserve timestamp backticks)
      formattedText = formattedText.replace(/`([^`]*\d{1,2}:\d{2}:\d{2}[^`]*)`/g, '`$1`'); // Keep timestamps as code
      formattedText = formattedText.replace(/`([^`]+)`/g, (match, content) => {
        // If it contains a timestamp, keep as code
        if (/\d{1,2}:\d{2}:\d{2}/.test(content)) {
          return match;
        }
        // Otherwise make it bold
        return `**${content}**`;
      });
      
      // Add proper structure with headers and sections
      formattedText = formattedText
        // Replace specific patterns with headers
        .replace(/^(The performance metrics provide.*?)(\w)/gm, '## System Performance Analysis\n\n$1$2')
        .replace(/(CPU exhaustion and severe resource contention)/g, '**$1**')
        .replace(/(HTTP 500 errors|performance degradation|functional failures)/g, '**$1**')
        
        // Add section breaks for major points
        .replace(/\. (This directly correlates|The system is struggling|The high CPU|Now I need to use|Initial Spike)/g, '.\n\n### Key Findings\n\n$1')
        
        // Format bullet points better
        .replace(/^\s*[-•]\s*/gm, '- ')
        
        // Clean up and add proper spacing
        .replace(/\n{3,}/g, '\n\n')
        .trim();
      
      // If text doesn't start with a header, add one
      if (!formattedText.startsWith('#')) {
        formattedText = '## Analysis Summary\n\n' + formattedText;
      }
      
      return formattedText;
    }
    
    if (typeof analysis === 'object') {
      return '## Analysis Data\n\n```json\n' + JSON.stringify(analysis, null, 2) + '\n```';
    }
    
    return String(analysis);
  };

  return (
    <div className="h-full overflow-y-auto space-y-6">
      {/* Analysis Status */}
      <div className="bg-gray-900 border-gray-200 border rounded-lg p-4">
        <div className="flex items-center space-x-3">
          <Brain className="w-6 h-6 text-purple-600" />
          <h2 className="text-xl font-semibold text-blue-400">Comprehensive Root Cause Analysis</h2>
        </div>
        
        <div className="mt-2 font-medium text-gray-600">
          {loading ? 'Running analysis...' : (analysisData && analysisData.status === 'completed' ? 'Analysis Complete' : 'Ready to analyze')}
        </div>
      </div>

      {/* Loading Spinner - Only show spinner while loading */}
      {loading && (
        <div className="bg-grey-50 border border-yellow-200 rounded-lg p-8">
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin"></div>
            </div>
            <div className="text-center">
              <h3 className="font-medium text-gray-800 mb-2">Running Analysis</h3>
              <p className="text-sm text-blue-600">Please wait while we analyze your system...</p>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysisData && analysisData.status === 'completed' && analysisData.analysis && (
        <div className="bg-gradient-to-b from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6 shadow-lg">
          <div className="flex items-center space-x-3 mb-6">
            <CheckCircle className="w-6 h-6 text-green-400" />
            <h3 className="text-lg font-semibold text-green-400">Analysis Results</h3>
          </div>
          
          <div className="bg-gray-900 rounded-lg p-6 border border-gray-600 max-h-[600px] overflow-y-auto shadow-inner">
            <div className="markdown-content space-y-4">
              <ReactMarkdown 
                remarkPlugins={[remarkGfm]}
                components={{
                  // Headers with better visual hierarchy
                  h1: ({children}) => (
                    <h1 className="text-2xl font-bold text-white mb-6 mt-8 first:mt-0 pb-3 border-b-2 border-green-400/30">
                      {children}
                    </h1>
                  ),
                  h2: ({children}) => (
                    <h2 className="text-xl font-semibold text-blue-300 mb-4 mt-8 first:mt-0 pb-2 border-b border-gray-600">
                      <span className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-blue-400 rounded-full"></span>
                        {children}
                      </span>
                    </h2>
                  ),
                  h3: ({children}) => (
                    <h3 className="text-lg font-medium text-green-300 mb-3 mt-6 first:mt-0">
                      <span className="flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-green-400 rounded-full"></span>
                        {children}
                      </span>
                    </h3>
                  ),
                  h4: ({children}) => (
                    <h4 className="text-base font-medium text-gray-300 mb-2 mt-4">
                      {children}
                    </h4>
                  ),
                  
                  // Improved paragraph styling
                  p: ({children}) => {
                    // Skip empty paragraphs
                    if (!children || (Array.isArray(children) && children.every(child => !child || child.toString().trim() === ''))) {
                      return null;
                    }
                    return (
                      <p className="text-gray-300 mb-4 leading-relaxed text-sm">
                        {children}
                      </p>
                    );
                  },
                  
                  // Enhanced lists with better spacing
                  ul: ({children}) => (
                    <ul className="list-none space-y-2 mb-4 ml-4">
                      {children}
                    </ul>
                  ),
                  ol: ({children}) => (
                    <ol className="list-decimal list-inside space-y-2 mb-4 ml-4 text-gray-300">
                      {children}
                    </ol>
                  ),
                  li: ({children}) => (
                    <li className="text-gray-300 text-sm flex items-start">
                      <span className="text-blue-400 mr-2 mt-1 flex-shrink-0">•</span>
                      <span>{children}</span>
                    </li>
                  ),
                  
                  // Improved code styling
                  code: ({inline, children}) => {
                    if (inline) {
                      return (
                        <code className="bg-blue-900/50 text-blue-200 px-2 py-1 rounded-md text-xs font-mono border border-blue-800/50 mx-1">
                          {children}
                        </code>
                      );
                    }
                    return (
                      <code className="block bg-gray-950 text-green-300 p-4 rounded-lg border border-gray-700 overflow-x-auto text-sm font-mono leading-relaxed shadow-inner">
                        {children}
                      </code>
                    );
                  },
                  
                  pre: ({children}) => (
                    <div className="my-6">
                      <div className="bg-gray-800 px-4 py-2 rounded-t-lg border-b border-gray-600">
                        <span className="text-xs text-gray-400 font-medium">Code Block</span>
                      </div>
                      <pre className="bg-gray-950 border border-gray-700 border-t-0 rounded-b-lg p-4 overflow-x-auto shadow-inner">
                        {children}
                      </pre>
                    </div>
                  ),
                  
                  // Enhanced blockquotes
                  blockquote: ({children}) => (
                    <blockquote className="border-l-4 border-blue-400 pl-6 py-2 my-4 bg-gray-800/50 rounded-r-lg text-gray-300 italic">
                      {children}
                    </blockquote>
                  ),
                  
                  // Better emphasis styling
                  strong: ({children}) => <strong className="font-bold text-white">{children}</strong>,
                  em: ({children}) => <em className="italic text-gray-200">{children}</em>,
                  
                  // Improved link styling
                  a: ({href, children}) => (
                    <a 
                      href={href} 
                      className="text-blue-400 hover:text-blue-300 underline decoration-dotted underline-offset-2 transition-colors" 
                      target="_blank" 
                      rel="noopener noreferrer"
                    >
                      {children}
                    </a>
                  ),
                  
                  // Enhanced table styling
                  table: ({children}) => (
                    <div className="overflow-x-auto mb-6">
                      <table className="w-full border-collapse border border-gray-600 rounded-lg overflow-hidden shadow-lg">
                        {children}
                      </table>
                    </div>
                  ),
                  thead: ({children}) => <thead className="bg-gray-800">{children}</thead>,
                  tbody: ({children}) => <tbody className="bg-gray-900/50">{children}</tbody>,
                  tr: ({children}) => <tr className="border-b border-gray-700 hover:bg-gray-800/30 transition-colors">{children}</tr>,
                  th: ({children}) => (
                    <th className="border-r border-gray-700 px-4 py-3 text-left text-gray-200 font-semibold text-sm bg-gray-800">
                      {children}
                    </th>
                  ),
                  td: ({children}) => (
                    <td className="border-r border-gray-700 px-4 py-3 text-gray-300 text-sm">
                      {children}
                    </td>
                  ),
                  
                  // Horizontal rule styling
                  hr: () => <hr className="border-gray-600 my-6" />,
                }}
              >
                {formatAnalysisContent(analysisData.analysis)}
              </ReactMarkdown>
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {analysisData && analysisData.status === 'error' && (
        <div className="bg-gray-900 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-4">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h3 className="font-medium text-red-800">Analysis Error</h3>
          </div>
          
          <div className="bg-gray-900 rounded-md p-4 border border-red-100">
            <p className="text-sm text-red-700">
              {analysisData.message || 'An error occurred during analysis'}
            </p>
          </div>
        </div>
      )}

      {/* No Analysis State */}
      {!loading && (!analysisData || (!analysisData.analysis && analysisData.status !== 'error')) && (
        <div className="text-center text-gray-500 py-8">
          <Brain className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-600 mb-2">No Analysis Available</h3>
          <p className="text-sm">Click "Run Root Cause Analysis" in the sidebar to start a comprehensive analysis</p>
        </div>
      )}
    </div>
  );
};

export default AnalysisPanel;