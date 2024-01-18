import warnings
warnings.filterwarnings("ignore")
import torch
import sys
import json
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.models import crnn_vgg16_bn, db_resnet50
from doctr.models.predictor import OCRPredictor
from doctr.models.detection.predictor import DetectionPredictor
from doctr.models.recognition.predictor import RecognitionPredictor
from doctr.models.preprocessor import PreProcessor

VOCABS = {}
VOCABS['bn'] = 'শ০ূৃৰজআঔঅঊিঢ়খ৵পঢই৳ফঽ৪লেঐযঃঈঠুধড়৲ৄথভটঁঋৱরডৢছ৴ঙওঘস১৹ণগ৷৩ত৮হ৭োষৎ৶কন৬চমৈা়ীৠঝএ৻ব৯য়উৌঞ৺২ংৣদ৫্ৗ-।'
VOCABS['gu'] = '૮લઔ૨સખાઑઈઋૐઓવૄ૦઼ઁનઞઊ૫ીશફણ૬૭બ૧રળૌુઠઐઉષપેઇઅૃઝજૉક૱૯ગઍદો૪ૅએંહડઘ૩ૂછઙઃઽટતધિૈયઢ્આમથચભ-'
VOCABS['pa'] = 'ਗ਼ਵਨਁਰਊਖਂਆਜੈਲੴਣ੧ਛਭਫ੮੯ਚਔੀਯਹਲ਼ਞ੩ੜਫ਼ੁਮ੫ਤੇਦਸ਼ਟੰ੭ਓਅਃਡਾਉਠੱਈ੦ੵਖ਼ਏਕਥ੬ਧੲੑਝਿ੨ਐਬਪਘਸ਼ਙੌਜ਼ੋਗ੍ੳਇ੪ੂਢ-।'
VOCABS['kn'] = 'ಚೕಒಉೖಂಲಾಝಟೆಅ೬ೇ೨ಬಡವಜಢಞಔಏಧಶಭತಳೀಕಐಈಠಪ೫ಣ೮ೞಆಯುಗೢಋದಘೂ್ೈ೦ಓಱಃಹ೯ೋಮ೭ೠಥಖಫಇರ೪ಛಙೣಿ೩ೌೄಷಌಸನ಼ಊಎ೧ೃೊ-'
VOCABS['ml'] = ' -ംഃഅആഇഈഉഊഋഌഎഏഐഒഓഔകഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരറലളഴവശഷസഹാിീുൂൃൄെേൈൊോൌ്ൗൠൡൢൣ൦൧൨൩൪൫൬൭൮൯൰൱൲൳൴൵൹ൺൻർൽൾൿ'
VOCABS['or'] = 'ଖ୯୬ୋଓଞ୍ଶ୪ଣଥଚରୄତଃେ୮ଆକଵୂନଦ୰ୖୢଜଉଳଅଁଲଯଔପ୭ଷଢଡ଼ଊୟମିୁ୧ଂ଼ୀବଟଭଢ଼୦ଘଠୗ୫ୡାଐ୨ଙହଈୱ୩ୃଛଏୌଗଫସଇଧଡଝୈୣୠଋ-।'
VOCABS['ta'] = 'ய௴ஷ௫ைெஸஎஈோவ௲ூு௭அ்ஶி௰ஹ௧ௐா௮ஔ௺சீண௩இனஆழ௪௯ஙஊதஜ௷௶மௌள௸ஐபநேற௬டஒ௹ஞஉஏகௗொர௱௵ஃ௨லஓ௳௦-'
VOCABS['te'] = '౦ఱకఆఋడత౯౻ిహౌ౭౽ఉ౮్ధఓగ౼మ౫ూౠఔాఇనైఁజీౄుేసశృఃఝఢరఠలోఞౘఅ౹౧ౢఛబ౸ఐయ౩ఖటచెొఊదఈషథభఏౙ౬౾ఎ౪ణఒప౨ఫంఘఙళవ౺-'
VOCABS['ur'] = 'ٱيأۃدےش‘زعكئںسحٰنؐةقذ؟ؔ۔—ًمھٗپغٖطإؒرڑصټٍگاؤجضْﷺچ‎ۓِّؓٹظىتڈ‍یُه،خو؛آفبؑلہثﺅ‌ژَۂءک‏'
VOCABS['hi'] = 'ॲऽऐथफएऎह८॥ॉम९ुँ१ं।षघठर॓ॼड़गछिॱटऩॄऑवल५ढ़य़अञसऔयण॑क़॒ौॽशऍ॰ूीऒॊख़उज़ॻॅ३ओऌळनॠ०ेढङ४़ॢग़पऊॐज२डैभझकआदबऋखॾ॔ोइ्धतफ़ईृःा६चऱऴ७-'
VOCABS['sa'] = 'ज़ऋुड़ऍऐक५टय४उः३ॠध९्७ू१वऌौॐॡॢइ६ाै८नृअंथढेखऔघग़०लजोईरञपफँझभषॅॄगतचहसीढ़आशए।म२दठङबिऊडओळछण़ऽ'
VOCABS['mr'] = 'अआइईउऊऋॠऌॡएऐओऔअंअःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवसहक्षड़ढ़फ़य़'
# HANDWRITTEN MODEL FILES MAP
H_MODELS={}
H_MODELS['bn'] = 'crnn_vgg16_bn_handwritten_bengali.pt'
H_MODELS['gu'] = 'crnn_vgg16_bn_handwritten_gujarati.pt'
H_MODELS['pa'] = 'crnn_vgg16_bn_handwritten_punjabi.pt'
H_MODELS['kn'] = 'crnn_vgg16_bn_handwritten_kannada.pt'
H_MODELS['ml'] = 'crnn_vgg16_bn_handwritten_malyalam.pt'
H_MODELS['or'] = 'crnn_vgg16_bn_handwritten_odia.pt'
H_MODELS['ta'] = 'crnn_vgg16_bn_handwritten_tamil.pt'
H_MODELS['te'] = 'crnn_vgg16_bn_handwritten_telugu.pt'
H_MODELS['ur'] = 'crnn_vgg16_bn_handwritten_urdu.pt'
H_MODELS['hi'] = 'crnn_vgg16_bn_handwritten_hindi.pt'
H_MODELS['sa'] = 'crnn_vgg16_bn_handwritten_sanskrit.pt'
H_MODELS['mr'] = 'crnn_vgg16_bn_handwritten_marathi.pt'

# PRINTED MODEL FILES MAP
V_MODELS={}
V_MODELS['bn'] = 'crnn_vgg16_bn_printed-bengali.pt'
V_MODELS['gu'] = 'crnn_vgg16_bn_printed-gujarati.pt'
V_MODELS['pa'] = 'crnn_vgg16_bn_printed-punjabi.pt'
V_MODELS['kn'] = 'crnn_vgg16_bn_printed-kannada.pt'
V_MODELS['ml'] = 'crnn_vgg16_bn_printed-malyalam.pt'
V_MODELS['or'] = 'crnn_vgg16_bn_printed-odia.pt'
V_MODELS['ta'] = 'crnn_vgg16_bn_printed-tamil.pt'
V_MODELS['te'] = 'crnn_vgg16_bn_printed-telugu.pt'
V_MODELS['ur'] = 'crnn_vgg16_bn_printed-urdu.pt'
V_MODELS['hi'] = 'crnn_vgg16_bn_printed-hindi.pt'
V_MODELS['sa'] = 'crnn_vgg16_bn_printed-sanskrit.pt'
V_MODELS['mr'] = 'crnn_vgg16_bn_printed-marathi.pt'

# TO INITIALIZE THE HANDWRITTEN MODELS
def initialize_handwritten_models(language):
    if language=='en':
        predictor = ocr_predictor(pretrained=True)
    else:
        det_model = db_resnet50(pretrained=True)
        det_predictor = DetectionPredictor(PreProcessor((1024, 1024), batch_size=1, mean=(0.798, 0.785, 0.772), std=(0.264, 0.2749, 0.287)), det_model)

        #Recognition model
        reco_model = crnn_vgg16_bn(pretrained=False, vocab= VOCABS[language])
        reco_param = torch.load(H_MODELS[language], map_location="cpu")
        reco_model.load_state_dict(reco_param)
        reco_predictor = RecognitionPredictor(PreProcessor((32, 128), preserve_aspect_ratio=True, batch_size=1, mean=(0.694, 0.695, 0.693), std=(0.299, 0.296, 0.301)), reco_model)

        predictor = OCRPredictor(det_predictor, reco_predictor)

    return predictor

# TO INITIALIZE THE PRINTED MODELS
def initialize_printed_models(language):
    if language=='en':
        predictor = ocr_predictor(pretrained=True)
    else:
        det_model = db_resnet50(pretrained=True)
        det_predictor = DetectionPredictor(PreProcessor((1024, 1024), batch_size=1, mean=(0.798, 0.785, 0.772), std=(0.264, 0.2749, 0.287)), det_model)

        #Recognition model
        reco_model = crnn_vgg16_bn(pretrained=False, vocab= VOCABS[language])
        reco_param = torch.load(V_MODELS[language], map_location="cpu")
        reco_model.load_state_dict(reco_param)
        reco_predictor = RecognitionPredictor(PreProcessor((32, 128), preserve_aspect_ratio=True, batch_size=1, mean=(0.694, 0.695, 0.693), std=(0.299, 0.296, 0.301)), reco_model)

        predictor = OCRPredictor(det_predictor, reco_predictor)

    return predictor

def predict(file_path,language,modality):
    print(f"Initialising {modality} model for {language} language")
    doc = DocumentFile.from_images(file_path)
    if modality=="handwritten":
        model=initialize_handwritten_models(language)
    else:
        model=initialize_printed_models(language)
    result = model(doc)
    return result.export()
def main():
    #system arguments are in following order: language>modality>filepath
    res = predict(sys.argv[1], sys.argv[2], sys.argv[3])
    with open("./data/output.json", "w") as f:
        json.dump(res, f)
if(__name__=="__main__"):
    main()