#!/usr/bin/env python3
"""
Example script demonstrating OnToology Local usage.
This script creates a simple example ontology and processes it.
"""

import tempfile
import os
from pathlib import Path
import subprocess
import sys


def create_example_ontology(output_dir: Path) -> Path:
    """Create a simple example ontology for demonstration."""
    
    ontology_content = """<?xml version="1.0"?>
<rdf:RDF xmlns="http://example.org/university#"
     xml:base="http://example.org/university"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:xml="http://www.w3.org/XML/1998/namespace"
     xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
    <owl:Ontology rdf:about="http://example.org/university">
        <dc:title>University Ontology</dc:title>
        <dc:description>A simple example ontology describing university concepts</dc:description>
        <dc:creator>OnToology Local Example</dc:creator>
        <owl:versionInfo>1.0</owl:versionInfo>
    </owl:Ontology>
    
    <!-- Classes -->
    <owl:Class rdf:about="#Person">
        <rdfs:label>Person</rdfs:label>
        <rdfs:comment>A human being</rdfs:comment>
    </owl:Class>
    
    <owl:Class rdf:about="#Student">
        <rdfs:label>Student</rdfs:label>
        <rdfs:comment>A person who is enrolled in educational courses</rdfs:comment>
        <rdfs:subClassOf rdf:resource="#Person"/>
    </owl:Class>
    
    <owl:Class rdf:about="#Professor">
        <rdfs:label>Professor</rdfs:label>
        <rdfs:comment>A person who teaches at a university</rdfs:comment>
        <rdfs:subClassOf rdf:resource="#Person"/>
    </owl:Class>
    
    <owl:Class rdf:about="#Course">
        <rdfs:label>Course</rdfs:label>
        <rdfs:comment>An educational course offered by the university</rdfs:comment>
    </owl:Class>
    
    <owl:Class rdf:about="#Department">
        <rdfs:label>Department</rdfs:label>
        <rdfs:comment>An academic department within the university</rdfs:comment>
    </owl:Class>
    
    <!-- Object Properties -->
    <owl:ObjectProperty rdf:about="#enrolledIn">
        <rdfs:label>enrolled in</rdfs:label>
        <rdfs:comment>Relates a student to a course they are enrolled in</rdfs:comment>
        <rdfs:domain rdf:resource="#Student"/>
        <rdfs:range rdf:resource="#Course"/>
    </owl:ObjectProperty>
    
    <owl:ObjectProperty rdf:about="#teaches">
        <rdfs:label>teaches</rdfs:label>
        <rdfs:comment>Relates a professor to a course they teach</rdfs:comment>
        <rdfs:domain rdf:resource="#Professor"/>
        <rdfs:range rdf:resource="#Course"/>
    </owl:ObjectProperty>
    
    <owl:ObjectProperty rdf:about="#belongsTo">
        <rdfs:label>belongs to</rdfs:label>
        <rdfs:comment>Relates a person to their department</rdfs:comment>
        <rdfs:domain rdf:resource="#Person"/>
        <rdfs:range rdf:resource="#Department"/>
    </owl:ObjectProperty>
    
    <!-- Datatype Properties -->
    <owl:DatatypeProperty rdf:about="#studentId">
        <rdfs:label>student ID</rdfs:label>
        <rdfs:comment>The unique identifier for a student</rdfs:comment>
        <rdfs:domain rdf:resource="#Student"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>
    
    <owl:DatatypeProperty rdf:about="#courseName">
        <rdfs:label>course name</rdfs:label>
        <rdfs:comment>The name of a course</rdfs:comment>
        <rdfs:domain rdf:resource="#Course"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#string"/>
    </owl:DatatypeProperty>
    
    <owl:DatatypeProperty rdf:about="#credits">
        <rdfs:label>credits</rdfs:label>
        <rdfs:comment>The number of credits for a course</rdfs:comment>
        <rdfs:domain rdf:resource="#Course"/>
        <rdfs:range rdf:resource="http://www.w3.org/2001/XMLSchema#integer"/>
    </owl:DatatypeProperty>
    
    <!-- Individuals -->
    <Student rdf:about="#john_doe">
        <rdfs:label>John Doe</rdfs:label>
        <studentId>S12345</studentId>
    </Student>
    
    <Professor rdf:about="#jane_smith">
        <rdfs:label>Prof. Jane Smith</rdfs:label>
    </Professor>
    
    <Course rdf:about="#cs101">
        <rdfs:label>Introduction to Computer Science</rdfs:label>
        <courseName>CS 101</courseName>
        <credits rdf:datatype="http://www.w3.org/2001/XMLSchema#integer">3</credits>
    </Course>
    
    <Department rdf:about="#computer_science">
        <rdfs:label>Computer Science Department</rdfs:label>
    </Department>
    
    <!-- Relationships -->
    <rdf:Description rdf:about="#john_doe">
        <enrolledIn rdf:resource="#cs101"/>
        <belongsTo rdf:resource="#computer_science"/>
    </rdf:Description>
    
    <rdf:Description rdf:about="#jane_smith">
        <teaches rdf:resource="#cs101"/>
        <belongsTo rdf:resource="#computer_science"/>
    </rdf:Description>
    
</rdf:RDF>"""
    
    ontology_file = output_dir / "university.owl"
    with open(ontology_file, 'w', encoding='utf-8') as f:
        f.write(ontology_content)
    
    return ontology_file


def run_example():
    """Run the complete example."""
    
    print("OnToology Local - Example Demonstration")
    print("=" * 50)
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_dir = temp_path / "ontologies"
        output_dir = temp_path / "documentation"
        
        input_dir.mkdir()
        
        print(f"Creating example ontology in: {input_dir}")
        ontology_file = create_example_ontology(input_dir)
        print(f"Created: {ontology_file}")
        
        # Run OnToology Local
        print(f"\nProcessing ontology with OnToology Local...")
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        
        try:
            # Run the CLI tool
            cmd = [
                sys.executable, "cli.py",
                "--input", str(input_dir),
                "--output", str(output_dir),
                "--verbose"
            ]
            
            print(f"\nRunning: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("\n✅ Processing completed successfully!")
                print("\nGenerated files:")
                
                # List generated files
                if output_dir.exists():
                    for file_path in sorted(output_dir.rglob("*")):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(output_dir)
                            print(f"  📄 {rel_path}")
                    
                    index_file = output_dir / "index.html"
                    if index_file.exists():
                        print(f"\n🌐 Open the documentation: file://{index_file.absolute()}")
                        
                        # Try to open in browser (optional)
                        try:
                            import webbrowser
                            webbrowser.open(f"file://{index_file.absolute()}")
                            print("   (Opened in default browser)")
                        except:
                            pass
                else:
                    print("❌ No output directory created")
                    
            else:
                print(f"\n❌ Processing failed with return code: {result.returncode}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
        except Exception as e:
            print(f"\n❌ Error running OnToology Local: {e}")
        
        print(f"\nExample files are in temporary directory: {temp_dir}")
        print("Press Enter to continue (files will be cleaned up)...")
        input()


if __name__ == "__main__":
    run_example()
