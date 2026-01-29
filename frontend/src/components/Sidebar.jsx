// // frontend/src/components/Sidebar.jsx
// import React from 'react';
// import { Trash2, FileText } from 'lucide-react';

// const Sidebar = ({ onClearChat }) => {
//   const examples = [
//     "What is the password policy?",
//     "Can I use personal email for work?",
//     "What's the remote work policy?",
//     "How often should I change my password?",
//     "What happens if I violate security policies?",
//   ];

//   return (
//     <div className="w-64 bg-gray-50 border-r border-gray-200 p-4 flex flex-col">
//       <div className="mb-6">
//         <h2 className="text-lg font-semibold text-gray-800 mb-2 flex items-center gap-2">
//           <FileText size={20} />
//           Quick Examples
//         </h2>
//         <div className="space-y-2">
//           {examples.map((example, idx) => (
//             <div
//               key={idx}
//               className="text-sm text-gray-600 p-2 bg-white rounded border border-gray-200 hover:border-blue-300 cursor-pointer transition-colors"
//             >
//               {example}
//             </div>
//           ))}
//         </div>
//       </div>

//       <div className="mt-auto">
//         <button
//           onClick={onClearChat}
//           className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
//         >
//           <Trash2 size={16} />
//           Clear Chat
//         </button>
//       </div>
//     </div>
//   );
// };

// export default Sidebar;