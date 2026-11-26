"""Evidence-led coauthor note. Does not read C01 scientific outcomes."""
from pathlib import Path
import json,hashlib,zipfile
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1];SG=ROOT.parent/'SGSMA26-Physics-Informed-AD'
X3=SG/'experiments/PAPER_RECOVERY_EXTERNAL_X03';X4=SG/'experiments/PAPER_RECOVERY_F01_X04'
def main():
    s=json.loads((X4/'results/SUMMARY.json').read_text());a=json.loads((X3/'REPRODUCTION.json').read_text());c=json.loads((X3/'audit/EXACT_GROUP_RESAMPLING.json').read_text())
    out=ROOT/'output/pdf/P07_Revision_Chat_y_Recuperacion_20261031.pdf'
    pdfmetrics.registerFont(TTFont('ReviewArial','C:/Windows/Fonts/arial.ttf'));pdfmetrics.registerFont(TTFont('ReviewArialBold','C:/Windows/Fonts/arialbd.ttf'))
    styles=getSampleStyleSheet()
    for name in ['Normal','BodyText','Title','Heading1','Heading2']:styles[name].fontName='ReviewArialBold' if name in ['Title','Heading1','Heading2'] else 'ReviewArial'
    styles['BodyText'].fontSize=10;styles['BodyText'].leading=14;styles['BodyText'].spaceAfter=8
    styles['Title'].fontSize=22;styles['Title'].leading=26
    styles.add(ParagraphStyle('SmallReview',fontName='ReviewArial',fontSize=8.2,leading=10.5))
    story=[]
    def para(t,style='BodyText'):story.append(Paragraph(t,styles[style]))
    def heading(t):para(t,'Heading1')
    def table(rows,widths):
        cell=[[Paragraph(str(x),styles['SmallReview']) for x in row] for row in rows]
        tab=Table(cell,colWidths=widths,hAlign='LEFT');tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7eff5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#466278')),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]));story.append(tab);story.append(Spacer(1,12))
    para('P07: qué aporta la nueva revisión','Title');para('Auditoría del chat público, reproducción externa y control físico F01 | 31 de octubre de 2026','SmallReview');story.append(Spacer(1,16))
    heading('La decisión científica')
    para('Conservar R11 como procedimiento causal de atribución de cargas y líneas sucesivas. Su comparación debe medir diagnósticos correctos antes de restauración, extras y cierre, además de detección. El nuevo chat no demuestra un algoritmo superior ni autoriza a cambiar C01.')
    para('<b>El giro atractivo que no se sostiene:</b> vender la recuperación como información adicional que mejora siempre la localización. La reproducción externa y el nuevo control Julia no muestran esa ventaja general. Retener la recuperación sigue siendo necesario para una predicción consistente; eso es distinto de aumentar la información disponible.')
    table([['Evidencia','Resultado','Lo que permite afirmar'],['X02 / F01','240/240 en ambas variantes corregidas; error de intensidad 1.2032% a 0.3288%','Mejora de intensidad en prueba de familia/ON/OFF conocidos; sin aciertos de origen adicionales.'],['X03 / modelo clásico externo','108 casos reproducidos; 14/14 controles','El paquete es reproducible; no es el modelo F01 ni R11.'],['X04 / F01 completo',f'{s["physical_trajectories"]} trayectorias; 12 comparaciones; 98.35% en ambas variantes','No mejora media de clasificación binaria en este control oráculo.'],['C01 / R11 y comparadores','Confirmación todavía en ejecución','No usar resultados parciales para ajustar ni reclamar una victoria.']],[105,163,244])
    para('Novedad acotada: el contrato concreto de intervención/restauración y la evaluación de atribución temporal. Sensibilidades DAE, Bayes, memoria de historias y tensores de pesos tienen antecedentes. Aún no hay demostración de superioridad frente a M3H con la misma física.')
    story.append(PageBreak())
    heading('Qué pasó en el modelo Julia real')
    para('38 trayectorias de 8 s, 241 reportes a 30 fps, una integración por trayectoria y cero reinicios. Carga previa +8% en BUS7 o BUS24, ON 2 s/OFF 3 s. Segunda carga +0.06%, tras 0.5 o 2 s; pares 18/27, 16/21 y 3/21, horizonte 1.5 s. Los 90 archivos protegidos comprobados permanecen idénticos.')
    story.append(Image(str(X4/'figures/recovery_information.png'),width=512,height=197));story.append(Spacer(1,10))
    para(f'La razón mediana de separación respecto al equilibrio es <b>{s["median_ratio_known"]:.4f}</b> con historia conocida y <b>{s["median_ratio_uncertain"]:.4f}</b> con una dirección incierta de severidad previa. Ninguna de las 12 razones de la segunda variante supera uno. Al añadir covarianza, la precisión a firma fija cae por construcción; el panel izquierdo separa ese efecto del cambio físico de firmas.')
    para('Ambas variantes binarias obtienen 98.3472% de media: un caso mejora 0.3333 puntos y dos pierden 0.1667. Son cambios de pocos draws, sin una conclusión de superioridad. Las 12 celdas comparten cuatro historias; los 7.200 draws no constituyen 7.200 trayectorias físicas independientes.')
    para('<b>Límite:</b> historia, onset, familia y pareja candidatos conocidos. Secantes finitas, no tangentes analíticas; ruido gaussiano en innovaciones y una sola dirección de incertidumbre, no un posterior causal completo. La distancia perfila amplitudes positivas; la evidencia integra amplitudes firmadas. No se deriva una probabilidad de error de esa distancia.')
    story.append(PageBreak())
    heading('Señales que explican la pregunta física')
    para('Caso ilustrativo fijado antes de analizar resultados: recuperación de BUS7, retardo de 0.5 s, dos posibles fuentes nuevas. Se resta el contrafactual de recuperación sin evento nuevo. Las curvas muestran el incremento que tendría que distinguir el diagnóstico, no voltajes o corrientes absolutas ni una comparación con RAW0001.')
    story.append(Image(str(X4/'figures/recovery_increment.png'),width=512,height=375))
    para('Las corrientes usan el terminal y la orientación F01. Frecuencia y ROCOF proceden de la cadena instrumental congelada; el análisis no sustituye frecuencia de bus por velocidad de rotor. BUS5 mantiene su hipótesis histórica provisional y BUS39 conserva sus límites.')
    heading('Por qué una línea puede parecer una perturbación nodal')
    para('A voltaje fijado, retirar una rama puede representarse mediante corrientes equivalentes en sus extremos. La identidad se verificó en las 46 ramas con error máximo 1.28e-13. Ocho ramas están directamente representadas por las corrientes terminales de F01. Las inyecciones equivalentes no tienen por qué ser cargas P/Q constantes ni trayectorias dinámicamente admisibles: esa restricción física es parte de la discriminación, no información creada por cambiar de notación.')
    story.append(PageBreak())
    heading('Qué adoptamos del chat y qué dejamos fuera')
    table([['Incorporado','No demostrado'],['Una historia central: intervención nueva frente a recuperación retenida.','Un nuevo estimador óptimo o una ventaja universal de recuperación.'],['Separar ajuste, intensidad, origen y calibración.','Posterior calibrado porque las masas suman uno.'],['M3H y Nagi/Huan/Chen como antecedentes explícitos.','Prioridad por usar DAE, Kirchhoff, Bayes o un tensor.'],['X03 reproducido, X04 ejecutado y resultados negativos visibles.','Superioridad de X04 frente a R11, M3H o el leaderboard completo.'],['Reglas del banco y orden predictivo aclarados en P07.','Adjuntos, soportes múltiples y refinamiento certificado implementados.']],[256,256])
    heading('Auditoría externa')
    para(f'El ZIP recibido pasa su manifiesto; la tabla de 108 casos se reproduce con diferencia máxima {a["max_absolute_difference"]:.2g}. Su intervalo original no incluía código de generación. Enumerar las 46.656 remuestras de seis grupos da [{c["exact_six_group_resampling_interval_pp"][0]:.3f}, {c["exact_six_group_resampling_interval_pp"][1]:.3f}] puntos, todavía descriptivo y compatible con cero. No es inferencia poblacional. Los tiempos de ejecución varían entre plataformas: no hay prueba general de aceleración.')
    heading('Qué falta antes del envío')
    para('1. Terminar C01 y verificar 171 trayectorias/342 registros, incluidos fallos, censuras, exposición normal e intervalos por padre. 2. Integrar las comparaciones completas de R11, nominal, ambos ExtraTrees y Chen en su contrato elegible. 3. Revisar las conclusiones con esos resultados sin retocar métodos. 4. Completar aprobación de coautores, afiliaciones, biografías y comprobación final de referencias/formato.')
    para('El manuscrito actualizado es una versión para revisión crítica de coautores, no una garantía de aceptación ni una declaración de envío listo. La figura de eventos y el unifilar protegidos se conservan. No se abrió RAW0002, no se recalibró y no se hizo push.')
    def footer(canvas,doc):
        canvas.setFont('ReviewArial',8);canvas.setFillColor(colors.HexColor('#536776'));canvas.drawString(42,24,'P07 | evidencia auditada; C01 permanece congelado');canvas.drawRightString(554,24,str(doc.page))
    SimpleDocTemplate(str(out),pagesize=(595.28,841.89),leftMargin=42,rightMargin=41,topMargin=40,bottomMargin=42,title='P07 - Revisión y control de recuperación',author='SGSMA research audit').build(story,onFirstPage=footer,onLaterPages=footer)
    print(out)
if __name__=='__main__':main()
