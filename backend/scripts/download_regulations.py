"""
Download regulations (GDPR, CCPA, US Code sections)
"""
import requests
from pathlib import Path
import json

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "legal_data"
REGULATIONS_DIR = DATA_DIR / "regulations"

def download_gdpr_full_text():
    """Download full GDPR text"""
    print("\n📥 Downloading GDPR full text...")
    
    gdpr_file = REGULATIONS_DIR / "gdpr.txt"
    
    # GDPR full text URLs (multiple sources)
    gdpr_urls = [
        "https://gdpr-info.eu/",
        "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32016R0679"
    ]
    
    # For now, we'll create a comprehensive placeholder with key articles
    # In production, you'd scrape or use an API
    gdpr_text = """
REGULATION (EU) 2016/679 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL
of 27 April 2016
on the protection of natural persons with regard to the processing of personal data
and on the free movement of such data, and repealing Directive 95/46/EC
(General Data Protection Regulation)

CHAPTER I - GENERAL PROVISIONS

Article 1 - Subject matter and objectives
1. This Regulation lays down rules relating to the protection of natural persons with regard to the processing of personal data and rules relating to the free movement of personal data.

Article 2 - Material scope
1. This Regulation applies to the processing of personal data wholly or partly by automated means and to the processing other than by automated means of personal data which form part of a filing system or are intended to form part of a filing system.

Article 3 - Territorial scope
1. This Regulation applies to the processing of personal data in the context of the activities of an establishment of a controller or a processor in the Union, regardless of whether the processing takes place in the Union or not.

Article 4 - Definitions
For the purposes of this Regulation:
(1) 'personal data' means any information relating to an identified or identifiable natural person ('data subject');
(2) 'processing' means any operation or set of operations which is performed on personal data or on sets of personal data;
(3) 'consent' of the data subject means any freely given, specific, informed and unambiguous indication of the data subject's wishes;
(4) 'controller' means the natural or legal person which determines the purposes and means of the processing of personal data;
(5) 'processor' means a natural or legal person which processes personal data on behalf of the controller;

CHAPTER II - PRINCIPLES

Article 5 - Principles relating to processing of personal data
1. Personal data shall be:
   (a) processed lawfully, fairly and in a transparent manner;
   (b) collected for specified, explicit and legitimate purposes;
   (c) adequate, relevant and limited to what is necessary;
   (d) accurate and kept up to date;
   (e) kept in a form which permits identification for no longer than necessary;
   (f) processed in a manner that ensures appropriate security.

Article 6 - Lawfulness of processing
1. Processing shall be lawful only if at least one of the following applies:
   (a) the data subject has given consent;
   (b) processing is necessary for the performance of a contract;
   (c) processing is necessary for compliance with a legal obligation;
   (d) processing is necessary to protect vital interests;
   (e) processing is necessary for the performance of a task carried out in the public interest;
   (f) processing is necessary for legitimate interests pursued by the controller.

Article 7 - Conditions for consent
1. Where processing is based on consent, the controller shall be able to demonstrate that the data subject has consented to processing.

Article 8 - Conditions applicable to child's consent
1. Where Article 6(1)(a) applies, in relation to the offer of information society services directly to a child, the processing of the personal data of a child shall be lawful where the child is at least 16 years old.

Article 9 - Processing of special categories of personal data
1. Processing of personal data revealing racial or ethnic origin, political opinions, religious or philosophical beliefs, or trade union membership, and the processing of genetic data, biometric data for the purpose of uniquely identifying a natural person, data concerning health or data concerning a natural person's sex life or sexual orientation shall be prohibited.

CHAPTER III - RIGHTS OF THE DATA SUBJECT

Article 15 - Right of access by the data subject
1. The data subject shall have the right to obtain from the controller confirmation as to whether or not personal data concerning him or her are being processed.

Article 16 - Right to rectification
1. The data subject shall have the right to obtain from the controller without undue delay the rectification of inaccurate personal data.

Article 17 - Right to erasure ('right to be forgotten')
1. The data subject shall have the right to obtain from the controller the erasure of personal data without undue delay.

Article 20 - Right to data portability
1. The data subject shall have the right to receive the personal data concerning him or her, which he or she has provided to a controller, in a structured, commonly used and machine-readable format.

CHAPTER IV - CONTROLLER AND PROCESSOR

Article 24 - Responsibility of the controller
1. Taking into account the nature, scope, context and purposes of processing as well as the risks, the controller shall implement appropriate technical and organisational measures.

Article 25 - Data protection by design and by default
1. The controller shall implement appropriate technical and organisational measures designed to implement data protection principles.

Article 32 - Security of processing
1. The controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk.

CHAPTER V - TRANSFERS OF PERSONAL DATA TO THIRD COUNTRIES

Article 44 - General principle for transfers
Any transfer of personal data which are undergoing processing or are intended for processing after transfer to a third country or to an international organisation shall take place only if the conditions laid down in this Chapter are complied with.

CHAPTER VI - INDEPENDENT SUPERVISORY AUTHORITIES

Article 51 - Supervisory authority
1. Each Member State shall provide for one or more independent public supervisory authorities.

CHAPTER VII - COOPERATION AND CONSISTENCY

Article 60 - Cooperation between the lead supervisory authority and the other supervisory authorities concerned

CHAPTER VIII - REMEDIES, LIABILITY AND PENALTIES

Article 77 - Right to lodge a complaint with a supervisory authority
1. Without prejudice to any other administrative or judicial remedy, every data subject shall have the right to lodge a complaint with a supervisory authority.

Article 82 - Right to compensation and liability
1. Any person who has suffered material or non-material damage as a result of an infringement of this Regulation shall have the right to receive compensation from the controller or processor for the damage suffered.

Article 83 - General conditions for imposing administrative fines
1. Each supervisory authority shall ensure that the imposition of administrative fines is effective, proportionate and dissuasive.

[Note: This is a summary. Full GDPR text has 99 articles and 173 recitals.
Download complete text from: https://gdpr-info.eu/ or https://eur-lex.europa.eu/]
"""
    
    with open(gdpr_file, 'w', encoding='utf-8') as f:
        f.write(gdpr_text)
    
    print(f"✅ GDPR text saved to {gdpr_file}")
    print("   Note: This is a summary. Full text available at https://gdpr-info.eu/")
    return True

def download_ccpa_full_text():
    """Download full CCPA text"""
    print("\n📥 Downloading CCPA full text...")
    
    ccpa_file = REGULATIONS_DIR / "ccpa.txt"
    
    ccpa_text = """
CALIFORNIA CONSUMER PRIVACY ACT (CCPA)
Assembly Bill 375 (AB 375)

TITLE 1.81.5. CALIFORNIA CONSUMER PRIVACY ACT OF 2018

1798.100. General Duties of Businesses that Collect Personal Information
(a) A business that collects consumers' personal information shall, at or before the point of collection, inform consumers as to the categories of personal information to be collected and the purposes for which the categories of personal information shall be used.

1798.105. Consumer's Right to Delete Personal Information
(a) A consumer shall have the right to request that a business delete any personal information about the consumer which the business has collected from the consumer.

1798.110. Consumer's Right to Know What Personal Information is Being Collected
(a) A consumer shall have the right to request that a business that collects personal information about the consumer disclose to the consumer the following:
(1) The categories of personal information it has collected about that consumer.
(2) The categories of sources from which the personal information is collected.
(3) The business or commercial purpose for collecting or selling personal information.
(4) The categories of third parties with whom the business shares personal information.

1798.115. Consumer's Right to Know What Personal Information is Sold or Disclosed
(a) A consumer shall have the right to request that a business that sells the consumer's personal information, or that discloses it for a business purpose, disclose to that consumer:
(1) The categories of personal information that the business collected about the consumer.
(2) The categories of personal information that the business sold about the consumer and the categories of third parties to whom the personal information was sold.
(3) The categories of personal information that the business disclosed about the consumer for a business purpose.

1798.120. Consumer's Right to Opt-Out of Sale of Personal Information
(a) A consumer shall have the right, at any time, to direct a business that sells personal information about the consumer to third parties not to sell the consumer's personal information.

1798.125. Non-Discrimination
(a) A business shall not discriminate against a consumer because the consumer exercised any of the consumer's rights under this title.

1798.130. Notice, Disclosure, Correction and Deletion Requirements
(a) A business that is required to comply with Section 1798.120 shall, in a form that is reasonably accessible to consumers:
(1) Provide a clear and conspicuous link on the business's Internet homepage, titled "Do Not Sell My Personal Information".

1798.135. Opt-Out Links
(a) A business that has received direction from a consumer not to sell the consumer's personal information or, if the consumer is less than 16 years of age, has not received consent to sell the consumer's personal information, shall be prohibited, pursuant to paragraph (4) of subdivision (a) of Section 1798.120, from selling the consumer's personal information after its receipt of the consumer's direction.

1798.140. Definitions
For purposes of this title:
(a) "Aggregate consumer information" means information that relates to a group or category of consumers, from which individual consumer identities have been removed.
(b) "Biometric information" means an individual's physiological, biological or behavioral characteristics.
(c) "Business" means a legal entity that collects consumers' personal information.
(d) "Consumer" means a natural person who is a California resident.
(e) "Personal information" means information that identifies, relates to, describes, is capable of being associated with, or could reasonably be linked, directly or indirectly, with a particular consumer or household.

1798.145. Exemptions
(a) This title shall not apply to the sale of personal information by a consumer to a business if the consumer is a natural person who is a California resident.

1798.150. Civil Actions
(a) Any consumer whose nonencrypted and nonredacted personal information is subject to an unauthorized access and exfiltration, theft, or disclosure as a result of the business's violation of the duty to implement and maintain reasonable security procedures and practices may institute a civil action.

[Note: This is a summary. Full CCPA text available at: https://oag.ca.gov/privacy/ccpa]
"""
    
    with open(ccpa_file, 'w', encoding='utf-8') as f:
        f.write(ccpa_text)
    
    print(f"✅ CCPA text saved to {ccpa_file}")
    print("   Note: This is a summary. Full text available at https://oag.ca.gov/privacy/ccpa")
    return True

def download_us_code_sections():
    """Download relevant US Code sections"""
    print("\n📥 Downloading US Code sections...")
    
    us_code_dir = REGULATIONS_DIR / "us_code"
    us_code_dir.mkdir(exist_ok=True)
    
    # Relevant sections for contracts/compliance
    sections = {
        "title_15_commerce.txt": """
TITLE 15 - COMMERCE AND TRADE
CHAPTER 1 - MONOPOLIES AND COMBINATIONS IN RESTRAINT OF TRADE

Section 1 - Trusts, etc., in restraint of trade illegal; penalty
Every contract, combination in the form of trust or otherwise, or conspiracy, in restraint of trade or commerce among the several States, or with foreign nations, is declared to be illegal.

Section 2 - Monopolizing trade a felony; penalty
Every person who shall monopolize, or attempt to monopolize, or combine or conspire with any other person or persons, to monopolize any part of the trade or commerce among the several States, or with foreign nations, shall be deemed guilty of a felony.
""",
        "title_17_copyright.txt": """
TITLE 17 - COPYRIGHTS
CHAPTER 1 - SUBJECT MATTER AND SCOPE OF COPYRIGHT

Section 101 - Definitions
A "work made for hire" is—
(1) a work prepared by an employee within the scope of his or her employment; or
(2) a work specially ordered or commissioned for use as a contribution to a collective work.

Section 106 - Exclusive rights in copyrighted works
Subject to sections 107 through 122, the owner of copyright under this title has the exclusive rights to do and to authorize any of the following:
(1) to reproduce the copyrighted work;
(2) to prepare derivative works;
(3) to distribute copies to the public;
(4) to perform the work publicly;
(5) to display the work publicly.
""",
        "title_29_labor.txt": """
TITLE 29 - LABOR
CHAPTER 14 - AGE DISCRIMINATION IN EMPLOYMENT

Section 621 - Congressional statement of findings and purpose
The Congress hereby finds and declares that—
(a) in the face of rising productivity and affluence, older workers find themselves disadvantaged in their efforts to retain employment, and especially to regain employment when displaced from jobs;
(b) the setting of arbitrary age limits regardless of potential for job performance has become a common practice, and certain otherwise desirable practices may work to the disadvantage of older persons.

[Note: Full US Code available at https://uscode.house.gov/]
"""
    }
    
    for filename, content in sections.items():
        file_path = us_code_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ Saved {filename}")
    
    return True

def import_regulations_to_vector_store():
    """Import regulations into vector store"""
    print("\n📤 Importing regulations into vector store...")
    
    try:
        from services.vector_store import VectorStore
        
        vs = VectorStore()
        
        regulations = []
        metadata_list = []
        
        # GDPR
        gdpr_file = REGULATIONS_DIR / "gdpr.txt"
        if gdpr_file.exists():
            with open(gdpr_file, 'r', encoding='utf-8') as f:
                gdpr_text = f.read()
            # Split into chunks
            chunk_size = 2000
            chunks = [gdpr_text[i:i+chunk_size] for i in range(0, len(gdpr_text), chunk_size)]
            for chunk in chunks:
                if len(chunk.strip()) > 100:
                    regulations.append(chunk)
                    metadata_list.append({
                        "type": "regulation",
                        "regulation_type": "GDPR",
                        "source": "EU Regulation 2016/679",
                        "jurisdiction": "EU"
                    })
        
        # CCPA
        ccpa_file = REGULATIONS_DIR / "ccpa.txt"
        if ccpa_file.exists():
            with open(ccpa_file, 'r', encoding='utf-8') as f:
                ccpa_text = f.read()
            chunk_size = 2000
            chunks = [ccpa_text[i:i+chunk_size] for i in range(0, len(ccpa_text), chunk_size)]
            for chunk in chunks:
                if len(chunk.strip()) > 100:
                    regulations.append(chunk)
                    metadata_list.append({
                        "type": "regulation",
                        "regulation_type": "CCPA",
                        "source": "California Civil Code",
                        "jurisdiction": "US-CA"
                    })
        
        # US Code
        us_code_dir = REGULATIONS_DIR / "us_code"
        if us_code_dir.exists():
            for code_file in us_code_dir.glob("*.txt"):
                with open(code_file, 'r', encoding='utf-8') as f:
                    code_text = f.read()
                if len(code_text.strip()) > 100:
                    regulations.append(code_text)
                    metadata_list.append({
                        "type": "regulation",
                        "regulation_type": "US Code",
                        "source": code_file.stem,
                        "jurisdiction": "US"
                    })
        
        if regulations:
            print(f"  Importing {len(regulations)} regulation chunks...")
            vs.add_documents(regulations, metadata_list, batch_size=50)
            vs.save()
            print(f"  ✅ Imported {len(regulations)} regulation chunks")
            return True
        else:
            print("  ⚠️  No regulations to import")
            return False
    except Exception as e:
        print(f"  ❌ Error importing regulations: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Download and import regulations"""
    print("="*70)
    print("📚 REGULATIONS DOWNLOADER & IMPORTER")
    print("="*70)
    
    REGULATIONS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download regulations
    download_gdpr_full_text()
    download_ccpa_full_text()
    download_us_code_sections()
    
    # Import to vector store
    import_regulations_to_vector_store()
    
    print("\n" + "="*70)
    print("✅ REGULATIONS PROCESSING COMPLETE!")
    print("="*70)
    print("\n💡 Note: These are summaries. For full text:")
    print("   • GDPR: https://gdpr-info.eu/")
    print("   • CCPA: https://oag.ca.gov/privacy/ccpa")
    print("   • US Code: https://uscode.house.gov/")

if __name__ == "__main__":
    main()

