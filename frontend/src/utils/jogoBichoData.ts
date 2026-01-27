
export interface GrupoBicho {
  id: number;
  nome: string;
  dezenas: string[];
  imagem: string;
}

export const GRUPOS_BICHO: GrupoBicho[] = [
  { id: 1, nome: 'Avestruz', dezenas: ['01', '02', '03', '04'], imagem: 'avestruz.png' },
  { id: 2, nome: 'Águia', dezenas: ['05', '06', '07', '08'], imagem: 'aguia.png' },
  { id: 3, nome: 'Burro', dezenas: ['09', '10', '11', '12'], imagem: 'burro.png' },
  { id: 4, nome: 'Borboleta', dezenas: ['13', '14', '15', '16'], imagem: 'borboleta.png' },
  { id: 5, nome: 'Cachorro', dezenas: ['17', '18', '19', '20'], imagem: 'cachorro.png' },
  { id: 6, nome: 'Cabra', dezenas: ['21', '22', '23', '24'], imagem: 'cabra.png' },
  { id: 7, nome: 'Carneiro', dezenas: ['25', '26', '27', '28'], imagem: 'carneiro.png' },
  { id: 8, nome: 'Camelo', dezenas: ['29', '30', '31', '32'], imagem: 'camelo.png' },
  { id: 9, nome: 'Cobra', dezenas: ['33', '34', '35', '36'], imagem: 'cobra.png' },
  { id: 10, nome: 'Coelho', dezenas: ['37', '38', '39', '40'], imagem: 'coelho.png' },
  { id: 11, nome: 'Cavalo', dezenas: ['41', '42', '43', '44'], imagem: 'cavalo.png' },
  { id: 12, nome: 'Elefante', dezenas: ['45', '46', '47', '48'], imagem: 'elefante.png' },
  { id: 13, nome: 'Galo', dezenas: ['49', '50', '51', '52'], imagem: 'galo.png' },
  { id: 14, nome: 'Gato', dezenas: ['53', '54', '55', '56'], imagem: 'gato.png' },
  { id: 15, nome: 'Jacaré', dezenas: ['57', '58', '59', '60'], imagem: 'jacare.png' },
  { id: 16, nome: 'Leão', dezenas: ['61', '62', '63', '64'], imagem: 'leao.png' },
  { id: 17, nome: 'Macaco', dezenas: ['65', '66', '67', '68'], imagem: 'macaco.png' },
  { id: 18, nome: 'Porco', dezenas: ['69', '70', '71', '72'], imagem: 'porco.png' },
  { id: 19, nome: 'Pavão', dezenas: ['73', '74', '75', '76'], imagem: 'pavao.png' },
  { id: 20, nome: 'Peru', dezenas: ['77', '78', '79', '80'], imagem: 'peru.png' },
  { id: 21, nome: 'Touro', dezenas: ['81', '82', '83', '84'], imagem: 'touro.png' },
  { id: 22, nome: 'Tigre', dezenas: ['85', '86', '87', '88'], imagem: 'tigre.png' },
  { id: 23, nome: 'Urso', dezenas: ['89', '90', '91', '92'], imagem: 'urso.png' },
  { id: 24, nome: 'Veado', dezenas: ['93', '94', '95', '96'], imagem: 'veado.png' },
  { id: 25, nome: 'Vaca', dezenas: ['97', '98', '99', '00'], imagem: 'vaca.png' },
];

export const getGrupoByNumero = (numero: string): GrupoBicho | undefined => {
  const num = parseInt(numero, 10);
  return GRUPOS_BICHO.find(g => g.id === num);
};
