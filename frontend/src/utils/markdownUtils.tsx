/**
 * Utility functions for processing and cleaning markdown content
 * Extracted for better testability and reusability
 */

import React from 'react';

export interface ParsedMarkdownSection {
  title: string;
  content: string;
  type: string;
}

/**
 * Cleans and processes investigation content by removing duplicate headers
 * and applying consistent formatting patterns
 */
export function cleanInvestigationContent(content: string): string {
  // FIRST: Remove the duplicate header patterns like "****: REGULATORY ANALYSIS:"
  let processedContent = content
    .replace(/^\*{4}:\s*(REGULATORY ANALYSIS|EVIDENCE COLLECTION|COMPLIANCE CHECK|FINAL REPORT):\s*/i, '')
    .trim();
  
  // AGGRESSIVE text breaking - split on multiple patterns simultaneously
  processedContent = processedContent
    // Break before risk/compliance patterns
    .replace(/Risk assessment:/gi, '|||BREAK|||**Risk assessment:**')
    .replace(/Regulatory compliance:/gi, '|||BREAK|||**Regulatory compliance:**')
    .replace(/Document analysis:/gi, '|||BREAK|||**Document analysis:**')
    .replace(/Web intelligence:/gi, '|||BREAK|||**Web intelligence:**')
    .replace(/Academic research:/gi, '|||BREAK|||**Academic research:**')
    .replace(/Suspicious indicators:/gi, '|||BREAK|||**Suspicious indicators:**')
    .replace(/Risk classification:/gi, '|||BREAK|||**Risk classification:**')
    .replace(/Summary:/gi, '|||BREAK|||**Summary:**')
    .replace(/Filing requirements:/gi, '|||BREAK|||**Filing requirements:**')
    .replace(/Key findings:/gi, '|||BREAK|||**Key findings:**')
    .replace(/Status:/gi, '|||BREAK|||**Status:**')
    
    // Break before numbered items
    .replace(/(\s)(\d+)\.\s+([A-Z])/g, '$1|||BREAK|||$2. $3')
    
    // Break before bullet points
    .replace(/(\s)•\s*/g, '$1|||BREAK|||• ')
    
    // Break before CFR regulations
    .replace(/(\s)(31\s+CFR|32\s+CFR)/gi, '$1|||BREAK|||$2')
    
    // Break before quotes
    .replace(/(\s)("[\w\s]+)/g, '$1|||BREAK|||$2');
  
  return processedContent;
}

/**
 * Splits processed content into segments and filters out empty ones
 */
export function splitContentIntoSegments(processedContent: string): string[] {
  return processedContent
    .split('|||BREAK|||')
    .map(segment => segment.trim())
    .filter(segment => segment.length > 0);
}

/**
 * Removes markdown formatting characters from text
 */
export function stripMarkdownFormatting(text: string): string {
  return text.replace(/\*\*/g, '');
}

/**
 * Parses markdown text and splits it by bold sections
 */
export function parseMarkdownBoldSections(text: string): (string | React.ReactElement)[] {
  const parts = text.split(/(\*\*.*?\*\*)/g);
  
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      const boldText = part.slice(2, -2);
      return <strong key={index} className="font-semibold text-gray-900 dark:text-gray-100">{boldText}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
}

/**
 * Checks if content has structured markdown sections
 */
export function hasStructuredSections(content: string): boolean {
  return content.includes('**') && content.split('**').length > 4;
}

/**
 * Splits content into structured sections for enhanced formatting
 */
export function splitIntoStructuredSections(content: string): string[] {
  return content.split(/(\*\*[A-Z\s]+\*\*:?)/g).filter(Boolean);
}

/**
 * Checks if a section is a header (starts and ends with **)
 */
export function isMarkdownHeader(section: string): boolean {
  return section.match(/^\*\*[A-Z\s]+\*\*:?$/) !== null;
}

/**
 * Extracts header text from markdown header section
 */
export function extractHeaderText(headerSection: string): string {
  return headerSection.replace(/\*\*/g, '').replace(':', '');
}

/**
 * Formats content for investigation results display
 */
export function formatContentForDisplay(content: string): ParsedMarkdownSection[] {
  return [{
    title: 'Investigation Analysis',
    content: content.trim(),
    type: 'info'
  }];
}
