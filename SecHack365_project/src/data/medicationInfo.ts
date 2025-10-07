/**
 * 薬の詳細情報データベース
 * 患者端末で自動表示される薬の情報
 */

export interface MedicationInfo {
  medicationName: string;
  genericName?: string;
  category: string;
  effect: string;
  detailedEffect: string;
  dosage: string;
  sideEffects: string[];
  precautions: string[];
  whenToTake: string;
  missedDose: string;
  interactions: string[];
}

export const medicationDatabase: Record<string, MedicationInfo> = {
  'カロナール': {
    medicationName: 'カロナール',
    genericName: 'アセトアミノフェン',
    category: '解熱鎮痛剤',
    effect: '熱を下げる、痛みを和らげる',
    detailedEffect: 'カロナールは、脳の体温調節中枢に作用して熱を下げ、痛みを感じにくくする薬です。比較的副作用が少なく、安全性の高い解熱鎮痛剤です。',
    dosage: '1回500mg、1日3回まで',
    sideEffects: [
      '発疹（まれ）',
      '吐き気（まれ）',
      '肝機能障害（長期大量服用時）',
      'アレルギー反応（非常にまれ）'
    ],
    precautions: [
      '肝臓病のある方は医師に相談',
      'アルコールとの併用は避ける',
      '空腹時の服用は避ける',
      '他の解熱剤との併用は避ける',
      '1日の最大量を守る'
    ],
    whenToTake: '食後30分以内に水またはぬるま湯で服用してください。',
    missedDose: '気づいた時点で1回分を服用してください。ただし、次の服用時間が近い場合は1回分を飛ばし、2回分を一度に服用しないでください。',
    interactions: [
      'アルコール: 肝臓への負担が増加',
      '他の解熱鎮痛剤: 効果が重複',
      'ワルファリン: 効果が増強される可能性'
    ]
  },
  'タミフル': {
    medicationName: 'タミフル',
    genericName: 'オセルタミビル',
    category: '抗インフルエンザ薬',
    effect: 'インフルエンザウイルスの増殖を抑える',
    detailedEffect: 'タミフルは、インフルエンザウイルスが細胞から出て広がるのを防ぐ薬です。発症後48時間以内に服用すると、症状の期間を短縮し、重症化を防ぐ効果があります。',
    dosage: '1回75mg、1日2回、5日間',
    sideEffects: [
      '吐き気・嘔吐（10-15%）',
      '腹痛・下痢（5-10%）',
      '頭痛（まれ）',
      '異常行動（非常にまれ、主に小児）'
    ],
    precautions: [
      '発症後48時間以内の服用が効果的',
      '処方された5日分は必ず飲み切る',
      '小児・未成年は異常行動に注意（保護者の見守り）',
      '腎機能が低下している方は医師に相談',
      '妊娠中・授乳中の方は医師に相談'
    ],
    whenToTake: '1日2回（朝・夕）、食後に服用してください。食後の服用により吐き気を軽減できます。',
    missedDose: '気づいた時点ですぐに1回分を服用してください。次の服用時間まで2時間以内の場合は、1回分を飛ばし、次回から通常通り服用してください。',
    interactions: [
      'インフルエンザワクチン: 併用可能',
      '解熱剤: 併用可能（医師の指示に従う）',
      '他の抗ウイルス薬: 医師に相談'
    ]
  },
  'ムコダイン': {
    medicationName: 'ムコダイン',
    genericName: 'カルボシステイン',
    category: '去痰剤',
    effect: '痰を出しやすくする',
    detailedEffect: 'ムコダインは、気道の粘液の成分を調整し、痰を出しやすくする薬です。鼻水や痰が多い時に効果的で、呼吸を楽にします。',
    dosage: '1回500mg、1日3回',
    sideEffects: [
      '胃の不快感（まれ）',
      '下痢（まれ）',
      '発疹（まれ）',
      '食欲不振（まれ）'
    ],
    precautions: [
      '胃潰瘍のある方は医師に相談',
      '十分な水分補給を心がける',
      '妊娠中・授乳中の方は医師に相談'
    ],
    whenToTake: '1日3回、食後に水またはぬるま湯で服用してください。',
    missedDose: '気づいた時点で1回分を服用してください。次の服用時間が近い場合は、1回分を飛ばしてください。',
    interactions: [
      '抗生物質: 併用可能',
      '解熱剤: 併用可能',
      '他の咳止め: 医師に相談'
    ]
  }
};

/**
 * 処方内容から薬情報を抽出
 */
export const extractMedicationsFromTreatment = (treatment: string): MedicationInfo[] => {
  const medications: MedicationInfo[] = [];
  
  for (const [name, info] of Object.entries(medicationDatabase)) {
    if (treatment.includes(name)) {
      medications.push(info);
    }
  }
  
  return medications;
};
