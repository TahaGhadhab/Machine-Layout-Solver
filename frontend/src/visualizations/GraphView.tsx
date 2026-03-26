import React, { useMemo } from 'react';

interface Props {
  groups: Record<string, number>;
  matrix: number[][]; // link_matrix
}

export const GraphView: React.FC<Props> = ({ groups, matrix }) => {
   const size = matrix.length;
   
   const nodes = useMemo(() => {
     const radius = 120;
     const center = 160;
     return Array.from({ length: size }).map((_, i) => {
       const angle = (i / size) * 2 * Math.PI - Math.PI / 2;
       return {
         id: i,
         x: center + radius * Math.cos(angle),
         y: center + radius * Math.sin(angle),
         group: groups[i.toString()] || 0
       };
     });
   }, [size, groups]);
   
   const colors = ['#8b5cf6', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#ef4444', '#6366f1'];
   
   return (
     <div className="w-full flex justify-center items-center p-4">
       <svg width="320" height="320" viewBox="0 0 320 320" className="drop-shadow-sm">
         {nodes.map((n1, i) => (
           nodes.slice(i+1).map((n2) => {
             const val = matrix[n1.id][n2.id];
             if (val === 0) return null;
             const strokeColor = val >= 2 ? '#ef4444' : '#fcd34d';
             const strokeWidth = val >= 2 ? 3 : 1;
             return (
               <line 
                 key={`link-${n1.id}-${n2.id}`} 
                 x1={n1.x} y1={n1.y} 
                 x2={n2.x} y2={n2.y} 
                 stroke={strokeColor} 
                 strokeWidth={strokeWidth}
                 opacity={0.6}
               />
             );
           })
         ))}
         {nodes.map(n => (
           <g key={n.id} className="transition-transform hover:scale-110 cursor-pointer" style={{ transformOrigin: `${n.x}px ${n.y}px` }}>
             <circle cx={n.x} cy={n.y} r={18} fill={colors[n.group % colors.length] || '#8b5cf6'} stroke="#fff" strokeWidth={3} className="dark:stroke-slate-800" />
             <text x={n.x} y={n.y} textAnchor="middle" dy=".3em" fill="#fff" fontSize={13} fontWeight="700">M{n.id + 1}</text>
           </g>
         ))}
       </svg>
     </div>
   );
};
