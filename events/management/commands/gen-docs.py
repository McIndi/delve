# Copyright (C) 2025 All rights reserved.
# This file is part of the Delve project, which is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the root of this repository for details.

from django.core.management.base import BaseCommand
from pathlib import Path
from markdown import markdown
import re

class Command(BaseCommand):
    help = 'Combines markdown documentation files into single files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default='html',
            choices=['html', 'md'],
            help='Output format (html or md)'
        )
        parser.add_argument(
            '--docs-dir',
            default='manuals',
            help='Root directory containing documentation'
        )

    def get_file_order(self, index_file):
        """Extract markdown file references from index.md"""
        if not index_file.exists():
            return []
        
        content = index_file.read_text(encoding='utf-8')
        # Look for markdown links like [Title](filename.md)
        matches = re.findall(r'\[.*?\]\((.*?\.md)\)', content)
        return [Path(match).stem for match in matches]

    def clean_content(self, content):
        """Remove navigation links from markdown content"""
        # Split content into lines
        lines = content.splitlines()
        
        # Remove navigation lines at the end (typically last 2-3 lines)
        while lines and any(
            pattern in lines[-1].lower() 
            for pattern in ['next:', 'previous:', '---']
        ):
            lines.pop()
        
        return '\n'.join(lines).strip()

    def handle(self, *args, **options):
        docs_dir = Path(options['docs_dir'])
        output_format = options['format']

        for manual_type in ['user', 'administration']:
            input_dir = docs_dir / manual_type
            if not input_dir.exists():
                self.stdout.write(
                    self.style.WARNING(
                        f'Directory not found: {input_dir}'
                    )
                )
                continue

            # Get file order from index.md
            index_file = input_dir / 'index.md'
            file_order = self.get_file_order(index_file)
            
            # Get all markdown files
            all_files = {f.stem: f for f in input_dir.glob("*.md")}
            
            if not all_files:
                self.stdout.write(
                    self.style.WARNING(
                        f'No markdown files found in {input_dir}'
                    )
                )
                continue

            # Combine content in the specified order
            combined_md = []
            
            # First add files in the order specified in index.md
            for file_stem in file_order:
                if file_stem in all_files:
                    file = all_files[file_stem]
                    self.stdout.write(f'Processing {file.name}...')
                    content = file.read_text(encoding='utf-8')
                    cleaned_content = self.clean_content(content)
                    combined_md.append(cleaned_content)
                    all_files.pop(file_stem)
            
            # Add any remaining files that weren't in the index
            for file in sorted(all_files.values()):
                if file.name != 'index.md':  # Skip the index file
                    self.stdout.write(f'Processing {file.name} (not in index)...')
                    content = file.read_text(encoding='utf-8')
                    cleaned_content = self.clean_content(content)
                    combined_md.append(cleaned_content)

            combined_content = "\n\n".join(combined_md)
            combined_content = markdown(
                combined_content,
                extensions=[
                    'codehilite',
                    'fenced_code',
                    'tables',
                ],
            )
            
            # Create output file
            output_file = docs_dir / f'{manual_type}_manual.{output_format}'
            
            if output_format == 'html':
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>{manual_type.title()} Manual</title>
                    <style>
                        body {{ max-width: 800px; margin: 40px auto; padding: 0 20px; }}
                    </style>
                </head>
                <body>
                    {combined_content}
                </body>
                </html>
                """
                output_file.write_text(html_content, encoding='utf-8')
            else:
                output_file.write_text(combined_content, encoding='utf-8')

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {output_file}'
                )
            )