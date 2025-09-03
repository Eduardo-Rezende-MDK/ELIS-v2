#!/usr/bin/env python3
"""
Sistema de Registro de Erros Simplificado
Armazena erros de sintaxe, causas e processos de resolução
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class ErrorRecord:
    """Registro de erro com informações completas"""
    id: str
    timestamp: str
    error_type: str  # syntax, runtime, logic, etc
    error_message: str
    code_snippet: str
    file_path: str
    line_number: int
    cause_analysis: str
    resolution_steps: List[str]
    fixed_code: str
    tags: List[str]
    severity: str  # low, medium, high, critical
    resolution_time_minutes: int
    
class ErrorRegistry:
    """Sistema de registro e busca de erros"""
    
    def __init__(self, storage_path: str = "error_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Arquivo JSON para armazenamento
        self.json_file = self.storage_path / "errors.json"
        
        # Carregar erros existentes
        self.errors = self._load_errors()
        
        print(f"Sistema de Registro de Erros inicializado com {len(self.errors)} erros")
    
    def _load_errors(self) -> List[ErrorRecord]:
        """Carrega erros do arquivo JSON"""
        if self.json_file.exists():
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [ErrorRecord(**error) for error in data]
            except Exception as e:
                print(f"Erro ao carregar registros: {e}")
        return []
    
    def _save_errors(self):
        """Salva erros no arquivo JSON"""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(error) for error in self.errors], f, 
                         ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar registros: {e}")
    
    def register_error(self, 
                      error_type: str,
                      error_message: str,
                      code_snippet: str,
                      file_path: str = "",
                      line_number: int = 0,
                      cause_analysis: str = "",
                      resolution_steps: List[str] = None,
                      fixed_code: str = "",
                      tags: List[str] = None,
                      severity: str = "medium",
                      resolution_time_minutes: int = 0) -> str:
        """Registra um novo erro no sistema"""
        
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.errors)}"
        
        error_record = ErrorRecord(
            id=error_id,
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_message,
            code_snippet=code_snippet,
            file_path=file_path,
            line_number=line_number,
            cause_analysis=cause_analysis,
            resolution_steps=resolution_steps or [],
            fixed_code=fixed_code,
            tags=tags or [],
            severity=severity,
            resolution_time_minutes=resolution_time_minutes
        )
        
        self.errors.append(error_record)
        self._save_errors()
        
        print(f"Erro registrado: {error_id}")
        return error_id
    
    def search_similar_errors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Busca erros similares usando busca por palavras-chave"""
        query_lower = query.lower()
        matches = []
        
        for error in self.errors:
            score = 0
            matched_fields = []
            
            # Buscar em diferentes campos com pesos diferentes
            if query_lower in error.error_message.lower():
                score += 5
                matched_fields.append("error_message")
            
            if query_lower in error.code_snippet.lower():
                score += 3
                matched_fields.append("code_snippet")
            
            if query_lower in error.cause_analysis.lower():
                score += 3
                matched_fields.append("cause_analysis")
            
            if any(query_lower in step.lower() for step in error.resolution_steps):
                score += 2
                matched_fields.append("resolution_steps")
            
            if any(query_lower in tag.lower() for tag in error.tags):
                score += 2
                matched_fields.append("tags")
            
            if query_lower in error.error_type.lower():
                score += 1
                matched_fields.append("error_type")
            
            # Busca por palavras individuais
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 2:  # Ignorar palavras muito pequenas
                    if word in error.error_message.lower():
                        score += 1
                    if word in error.cause_analysis.lower():
                        score += 1
            
            if score > 0:
                matches.append({
                    'error_record': error,
                    'similarity_score': score,
                    'matched_text': f"Campos encontrados: {', '.join(matched_fields)}"
                })
        
        # Ordenar por score e retornar top_k
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        return matches[:top_k]
    
    def get_error_by_id(self, error_id: str) -> Optional[ErrorRecord]:
        """Busca erro por ID"""
        return next((e for e in self.errors if e.id == error_id), None)
    
    def get_errors_by_type(self, error_type: str) -> List[ErrorRecord]:
        """Busca erros por tipo"""
        return [e for e in self.errors if e.error_type.lower() == error_type.lower()]
    
    def get_errors_by_severity(self, severity: str) -> List[ErrorRecord]:
        """Busca erros por severidade"""
        return [e for e in self.errors if e.severity.lower() == severity.lower()]
    
    def get_recent_errors(self, days: int = 7) -> List[ErrorRecord]:
        """Busca erros recentes"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent = []
        for error in self.errors:
            try:
                error_date = datetime.fromisoformat(error.timestamp)
                if error_date >= cutoff_date:
                    recent.append(error)
            except:
                continue
        
        return sorted(recent, key=lambda x: x.timestamp, reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Estatísticas do registro de erros"""
        if not self.errors:
            return {'total_errors': 0}
        
        # Contar por tipo
        types_count = {}
        severity_count = {}
        total_resolution_time = 0
        tags_count = {}
        
        for error in self.errors:
            types_count[error.error_type] = types_count.get(error.error_type, 0) + 1
            severity_count[error.severity] = severity_count.get(error.severity, 0) + 1
            total_resolution_time += error.resolution_time_minutes
            
            for tag in error.tags:
                tags_count[tag] = tags_count.get(tag, 0) + 1
        
        return {
            'total_errors': len(self.errors),
            'errors_by_type': types_count,
            'errors_by_severity': severity_count,
            'most_common_tags': dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            'average_resolution_time': total_resolution_time / len(self.errors) if self.errors else 0,
            'total_resolution_time': total_resolution_time
        }
    
    def get_resolution_patterns(self) -> Dict[str, Any]:
        """Analisa padrões de resolução"""
        patterns = {}
        
        for error in self.errors:
            if error.resolution_steps:
                first_step = error.resolution_steps[0] if error.resolution_steps else "N/A"
                key = f"{error.error_type}_{error.severity}"
                
                if key not in patterns:
                    patterns[key] = {
                        'count': 0,
                        'common_first_steps': {},
                        'avg_resolution_time': 0,
                        'total_time': 0
                    }
                
                patterns[key]['count'] += 1
                patterns[key]['total_time'] += error.resolution_time_minutes
                patterns[key]['avg_resolution_time'] = patterns[key]['total_time'] / patterns[key]['count']
                
                if first_step in patterns[key]['common_first_steps']:
                    patterns[key]['common_first_steps'][first_step] += 1
                else:
                    patterns[key]['common_first_steps'][first_step] = 1
        
        return patterns
    
    def export_report(self, output_file: str = None) -> str:
        """Exporta relatório completo de erros"""
        if not output_file:
            output_file = self.storage_path / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_statistics(),
            'resolution_patterns': self.get_resolution_patterns(),
            'recent_errors': [asdict(e) for e in self.get_recent_errors(30)],
            'all_errors': [asdict(error) for error in self.errors]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return str(output_file)
    
    def suggest_solution(self, error_message: str, code_snippet: str = "") -> List[Dict[str, Any]]:
        """Sugere soluções baseadas em erros similares"""
        # Buscar erros similares
        query = f"{error_message} {code_snippet}"
        similar_errors = self.search_similar_errors(query, top_k=3)
        
        suggestions = []
        for result in similar_errors:
            error = result['error_record']
            if error.resolution_steps:
                suggestions.append({
                    'similarity_score': result['similarity_score'],
                    'error_type': error.error_type,
                    'cause': error.cause_analysis,
                    'resolution_steps': error.resolution_steps,
                    'fixed_code': error.fixed_code,
                    'resolution_time': error.resolution_time_minutes
                })
        
        return suggestions

# Funções de conveniência
def register_syntax_error(error_msg: str, code: str, file_path: str = "", 
                         line_num: int = 0, solution_steps: List[str] = None) -> str:
    """Função rápida para registrar erro de sintaxe"""
    registry = ErrorRegistry()
    return registry.register_error(
        error_type="syntax",
        error_message=error_msg,
        code_snippet=code,
        file_path=file_path,
        line_number=line_num,
        resolution_steps=solution_steps or []
    )

def search_error_solutions(query: str) -> List[Dict[str, Any]]:
    """Função rápida para buscar soluções de erros"""
    registry = ErrorRegistry()
    return registry.search_similar_errors(query)

def get_solution_suggestions(error_msg: str, code: str = "") -> List[Dict[str, Any]]:
    """Função rápida para obter sugestões de solução"""
    registry = ErrorRegistry()
    return registry.suggest_solution(error_msg, code)

if __name__ == "__main__":
    # Exemplo de uso
    registry = ErrorRegistry()
    
    # Registrar um erro de exemplo
    error_id = registry.register_error(
        error_type="syntax",
        error_message="SyntaxError: invalid syntax",
        code_snippet="print('Hello World'",
        file_path="test.py",
        line_number=1,
        cause_analysis="Parênteses não fechado na função print",
        resolution_steps=[
            "Identificar parênteses não fechado",
            "Adicionar parênteses de fechamento",
            "Testar código corrigido"
        ],
        fixed_code="print('Hello World')",
        tags=["python", "print", "parenteses"],
        severity="low",
        resolution_time_minutes=2
    )
    
    print(f"Erro registrado: {error_id}")
    
    # Buscar erros similares
    results = registry.search_similar_errors("syntax error print")
    print(f"Encontrados {len(results)} erros similares")
    
    # Sugerir soluções
    suggestions = registry.suggest_solution("SyntaxError: invalid syntax", "print('test'")
    print(f"Sugestões: {len(suggestions)}")
    
    # Estatísticas
    stats = registry.get_statistics()
    print(f"Estatísticas: {stats}")