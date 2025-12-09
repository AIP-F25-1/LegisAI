import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface ClauseRisk {
  clause_id: string;
  clause_text: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  risk_score: number;
  risk_type: string;
  issues: string[];
  recommendations: string[];
}

interface RiskHeatmapProps {
  clauseRisks: ClauseRisk[];
  documentRiskLevel?: string;
  averageRiskScore?: number;
  onClauseClick?: (clause: ClauseRisk) => void;
}

const RiskHeatmap: React.FC<RiskHeatmapProps> = ({
  clauseRisks,
  documentRiskLevel,
  averageRiskScore,
  onClauseClick
}) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedClause, setSelectedClause] = useState<ClauseRisk | null>(null);
  const [hoveredClause, setHoveredClause] = useState<ClauseRisk | null>(null);

  useEffect(() => {
    if (!svgRef.current || clauseRisks.length === 0) return;

    // Clear previous render
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current);
    const width = svgRef.current.clientWidth || 800;
    const height = Math.max(400, clauseRisks.length * 60);
    // Increased right margin to make room for legend
    const margin = { top: 40, right: 180, bottom: 40, left: 250 };
    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    svg.attr('width', width).attr('height', height);

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Color scale for risk levels (defined inside useEffect to avoid dependency issues)
    const getColorForRiskLevel = (level: string): string => {
      const colorMap: Record<string, string> = {
        'low': '#10b981',      // green
        'medium': '#f59e0b',   // yellow
        'high': '#ef4444',     // red
        'critical': '#7c2d12'  // dark red
      };
      return colorMap[level] || '#6b7280';
    };

    // Risk score scale for intensity
    const intensityScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0.3, 1]);

    // X scale for risk score
    const xScale = d3.scaleLinear()
      .domain([0, 1])
      .range([0, innerWidth]);

    // Y scale for clauses
    const yScale = d3.scaleBand()
      .domain(clauseRisks.map((_, i) => i.toString()))
      .range([0, innerHeight])
      .padding(0.1);

    // Create gradient definitions for heatmap cells
    const defs = svg.append('defs');
    
    ['low', 'medium', 'high', 'critical'].forEach((level) => {
      const gradient = defs.append('linearGradient')
        .attr('id', `gradient-${level}`)
        .attr('x1', '0%')
        .attr('x2', '100%')
        .attr('y1', '0%')
        .attr('y2', '0%');

      const color = getColorForRiskLevel(level);
      gradient.append('stop')
        .attr('offset', '0%')
        .attr('stop-color', color)
        .attr('stop-opacity', 0.3);
      gradient.append('stop')
        .attr('offset', '100%')
        .attr('stop-color', color)
        .attr('stop-opacity', 1);
    });

    // Draw heatmap cells
    const cells = g.selectAll('.heatmap-cell')
      .data(clauseRisks)
      .enter()
      .append('rect')
      .attr('class', 'heatmap-cell')
      .attr('x', 0)
      .attr('y', (_, i) => yScale(i.toString()) || 0)
      .attr('width', d => xScale(d.risk_score))
      .attr('height', yScale.bandwidth())
      .attr('fill', d => {
        const intensity = intensityScale(d.risk_score);
        const color = getColorForRiskLevel(d.risk_level);
        return d3.color(color)?.brighter(1 - intensity).toString() || color;
      })
      .attr('stroke', d => getColorForRiskLevel(d.risk_level))
      .attr('stroke-width', 2)
      .attr('rx', 4)
      .style('cursor', 'pointer')
      .on('mouseover', function(event, d) {
        setHoveredClause(d);
        d3.select(this)
          .attr('stroke-width', 3)
          .attr('opacity', 0.8);
      })
      .on('mouseout', function() {
        setHoveredClause(null);
        d3.select(this)
          .attr('stroke-width', 2)
          .attr('opacity', 1);
      })
      .on('click', function(event, d) {
        setSelectedClause(d);
        if (onClauseClick) {
          onClauseClick(d);
        }
      });

    // Helper function to extract a clean clause title
    const getClauseTitle = (clauseText: string, clauseId: string): string => {
      let text = clauseText.trim();
      
      // Skip document titles (all caps, very long, or common title patterns)
      if (text === text.toUpperCase() && text.length > 30) {
        // This is likely a document title, extract from clause_id or use generic
        const idMatch = clauseId.match(/clause_(\d+)/);
        return idMatch ? `Clause ${idMatch[1]}` : 'Document Section';
      }
      
      // Pattern 1: Numbered sub-clauses (e.g., "4.1 Non-Compete:", "5.2 One-Way Indemnity:")
      const numberedSubClause = text.match(/^(\d+\.\d+\s+[^:\.]+?)(?::|\.|$)/);
      if (numberedSubClause) {
        return numberedSubClause[1].trim();
      }
      
      // Pattern 2: Numbered main clauses (e.g., "1. SCOPE OF SERVICES", "2. PAYMENT TERMS")
      const numberedMainClause = text.match(/^(\d+\.\s+[A-Z][^:\.]{3,40}?)(?::|\.|$)/);
      if (numberedMainClause) {
        return numberedMainClause[1].trim();
      }
      
      // Pattern 3: Named clauses with colon (e.g., "Indemnity:", "Termination:")
      const namedClause = text.match(/^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*):/);
      if (namedClause && namedClause[1].length > 3 && namedClause[1].length < 50) {
        return namedClause[1].trim();
      }
      
      // Pattern 4: Extract meaningful phrase from first sentence (skip generic starts)
      const skipPatterns = /^(this|the|a|an|that|these|those|client|provider|party|parties|agreement|agreements)\s+/i;
      let firstSentence = text.split(/[.:]/)[0].trim();
      
      // Remove common document boilerplate
      if (firstSentence.match(/^(agreement|this agreement|the agreement).*entered into/i)) {
        // Skip to next meaningful part
        const nextPart = text.split(/[.:]/).slice(1).join('.').trim();
        if (nextPart.length > 10) {
          firstSentence = nextPart.split(/[.:]/)[0].trim();
        }
      }
      
      // Clean up first sentence
      firstSentence = firstSentence.replace(skipPatterns, '').trim();
      
      if (firstSentence.length > 5 && firstSentence.length <= 50 && !/^\d+$/.test(firstSentence)) {
        // Capitalize first letter
        return firstSentence.charAt(0).toUpperCase() + firstSentence.slice(1);
      }
      
      // Pattern 5: Extract meaningful words (skip common words and generic numbers)
      const words = text.split(/\s+/);
      let meaningfulWords: string[] = [];
      let skipWords = ['this', 'the', 'a', 'an', 'that', 'these', 'those', 'client', 'provider', 
                       'party', 'parties', 'agreement', 'agreements', 'shall', 'will', 'may', 
                       'must', 'agrees', 'agree', 'agreed'];
      
      for (const word of words) {
        const cleanWord = word.replace(/[.,:;!?()\[\]{}]/g, '');
        // Skip if it's just a number or too short or in skip list
        if (cleanWord.length > 2 && 
            !skipWords.includes(cleanWord.toLowerCase()) && 
            !/^\d+$/.test(cleanWord) &&
            cleanWord.length < 20) {
          meaningfulWords.push(cleanWord);
          if (meaningfulWords.length >= 3 && meaningfulWords.join(' ').length >= 20) {
            break;
          }
        }
      }
      
      if (meaningfulWords.length >= 2) {
        const result = meaningfulWords.join(' ');
        return result.length > 50 ? result.substring(0, 47) + '...' : result;
      }
      
      // Pattern 6: If it's just a number, use clause_id
      if (/^\d+$/.test(text.trim())) {
        const idMatch = clauseId.match(/clause_(\d+)/);
        return idMatch ? `Clause ${idMatch[1]}` : clauseId;
      }
      
      // Fallback: Use clause number from ID
      const idMatch = clauseId.match(/clause_(\d+)/);
      const fallbackText = text.substring(0, 40).trim();
      if (fallbackText.length > 5) {
        return fallbackText;
      }
      return idMatch ? `Clause ${idMatch[1]}` : clauseId;
    };

    // Add clause labels
    g.selectAll('.clause-label')
      .data(clauseRisks)
      .enter()
      .append('text')
      .attr('class', 'clause-label')
      .attr('x', -10)
      .attr('y', (_, i) => (yScale(i.toString()) || 0) + yScale.bandwidth() / 2)
      .attr('text-anchor', 'end')
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '12px')
      .attr('fill', '#ffffff')
      .attr('font-weight', '500')
      .text(d => {
        const title = getClauseTitle(d.clause_text, d.clause_id);
        // Truncate if too long
        return title.length > 50 ? title.substring(0, 47) + '...' : title;
      });

    // Add risk score labels
    g.selectAll('.risk-score-label')
      .data(clauseRisks)
      .enter()
      .append('text')
      .attr('class', 'risk-score-label')
      .attr('x', d => xScale(d.risk_score) + 5)
      .attr('y', (_, i) => (yScale(i.toString()) || 0) + yScale.bandwidth() / 2)
      .attr('alignment-baseline', 'middle')
      .attr('font-size', '11px')
      .attr('font-weight', 'bold')
      .attr('fill', '#ffffff')
      .text(d => `${(d.risk_score * 100).toFixed(1)}%`);

    // Add X axis
    const xAxis = d3.axisBottom(xScale)
      .ticks(5)
      .tickFormat(d3.format('.0%'));
    
    const axisGroup = g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(xAxis);
    
    // Style axis elements
    axisGroup.selectAll('text')
      .attr('fill', '#ffffff')
      .attr('font-size', '11px');
    
    axisGroup.selectAll('path, line')
      .attr('stroke', '#ffffff')
      .attr('stroke-width', 1);
    
    g.append('text')
      .attr('x', innerWidth / 2)
      .attr('y', innerHeight + 35)
      .attr('text-anchor', 'middle')
      .attr('fill', '#ffffff')
      .attr('font-size', '12px')
      .attr('font-weight', 'bold')
      .text('Risk Score');

    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 20)
      .attr('text-anchor', 'middle')
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .attr('fill', '#ffffff')
      .text('Clause Risk Heatmap');

    // Add legend - positioned to avoid overlap with heatmap cells
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 170}, ${margin.top})`);

    const legendData = [
      { level: 'low', label: 'Low Risk' },
      { level: 'medium', label: 'Medium Risk' },
      { level: 'high', label: 'High Risk' },
      { level: 'critical', label: 'Critical Risk' }
    ];

    // Add legend background for better visibility
    legend.append('rect')
      .attr('x', -5)
      .attr('y', -5)
      .attr('width', 150)
      .attr('height', legendData.length * 25 + 10)
      .attr('fill', 'rgba(0, 0, 0, 0.3)')
      .attr('rx', 4);

    legend.selectAll('.legend-item')
      .data(legendData)
      .enter()
      .append('g')
      .attr('class', 'legend-item')
      .attr('transform', (_, i) => `translate(0, ${i * 25})`)
      .each(function(d) {
        const g = d3.select(this);
        g.append('rect')
          .attr('width', 15)
          .attr('height', 15)
          .attr('fill', getColorForRiskLevel(d.level))
          .attr('rx', 2);
        g.append('text')
          .attr('x', 20)
          .attr('y', 12)
          .attr('font-size', '11px')
          .attr('fill', '#ffffff')
          .text(d.label);
      });

  }, [clauseRisks, documentRiskLevel, averageRiskScore]);

  return (
    <div className="w-full">
      {/* Info Note */}
      <div className="mb-4 p-3 liquid-glass-card glass-content border-blue-500/30">
        <p className="text-xs text-white/80">
          <strong className="text-white">Clause Risk Heatmap:</strong> Each row represents a clause from your document. 
          The colored bar shows the risk score (0-100%). Click on a clause to see detailed analysis.
        </p>
      </div>

      {/* Summary Stats */}
      {documentRiskLevel && (
        <div className="mb-4 p-4 liquid-glass-card glass-content">
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-white/80">Document Risk Level</p>
              <p className={`text-2xl font-bold ${
                documentRiskLevel === 'critical' ? 'text-red-300' :
                documentRiskLevel === 'high' ? 'text-red-400' :
                documentRiskLevel === 'medium' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {documentRiskLevel.toUpperCase()}
              </p>
            </div>
            {averageRiskScore !== undefined && (
              <div>
                <p className="text-sm text-white/80">Average Risk Score</p>
                <p className="text-2xl font-bold text-white">
                  {(averageRiskScore * 100).toFixed(1)}%
                </p>
              </div>
            )}
            <div>
              <p className="text-sm text-white/80">Total Clauses</p>
              <p className="text-2xl font-bold text-white">
                {clauseRisks.length}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Heatmap */}
      <div className="liquid-glass-card glass-content p-4 overflow-x-auto">
        <svg ref={svgRef} className="w-full" style={{ minHeight: '400px' }} />
      </div>

      {/* Hover Tooltip */}
      {hoveredClause && (
        <div className="mt-4 p-4 liquid-glass-card glass-content border-blue-500/30">
          <h4 className="font-semibold text-white mb-2">
            {hoveredClause.clause_text.substring(0, 60)}...
          </h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-white/80">Risk Level:</p>
              <p className="font-semibold text-white">{hoveredClause.risk_level.toUpperCase()}</p>
            </div>
            <div>
              <p className="text-white/80">Risk Score:</p>
              <p className="font-semibold text-white">{(hoveredClause.risk_score * 100).toFixed(1)}%</p>
            </div>
            <div>
              <p className="text-white/80">Risk Type:</p>
              <p className="font-semibold text-white">{hoveredClause.risk_type}</p>
            </div>
            <div>
              <p className="text-white/80">Issues Found:</p>
              <p className="font-semibold text-white">{hoveredClause.issues.length}</p>
            </div>
          </div>
        </div>
      )}

      {/* Selected Clause Details */}
      {selectedClause && (
        <div className="mt-4 p-6 liquid-glass-card glass-content border-blue-500/30">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-lg font-bold text-white">Clause Details</h3>
            <button
              onClick={() => setSelectedClause(null)}
              className="text-white/80 hover:text-white"
            >
              ✕
            </button>
          </div>
          
          <div className="mb-4">
            <p className="text-sm text-white/80 mb-1">Clause Text:</p>
            <p className="text-white">{selectedClause.clause_text}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p className="text-sm text-white/80">Risk Level</p>
              <p className={`font-bold text-lg ${
                selectedClause.risk_level === 'critical' ? 'text-red-300' :
                selectedClause.risk_level === 'high' ? 'text-red-400' :
                selectedClause.risk_level === 'medium' ? 'text-yellow-400' :
                'text-green-400'
              }`}>
                {selectedClause.risk_level.toUpperCase()}
              </p>
            </div>
            <div>
              <p className="text-sm text-white/80">Risk Score</p>
              <p className="font-bold text-lg text-white">
                {(selectedClause.risk_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {selectedClause.issues.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-semibold text-white mb-2">⚠️ Issues Found:</p>
              <ul className="list-disc list-inside space-y-1">
                {selectedClause.issues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-red-300">{issue}</li>
                ))}
              </ul>
            </div>
          )}

          {selectedClause.recommendations.length > 0 && (
            <div>
              <p className="text-sm font-semibold text-white mb-2">💡 Recommendations:</p>
              <ul className="list-disc list-inside space-y-1">
                {selectedClause.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-green-300">{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RiskHeatmap;
