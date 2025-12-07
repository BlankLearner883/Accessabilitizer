FFmpeg 64-bit static Windows build from www.gyan.dev

Version: 2025-12-04-git-d6458f6a8b-full_build-www.gyan.dev

License: GPL v3

Source Code: https://github.com/FFmpeg/FFmpeg/commit/d6458f6a8b

External Assets
frei0r plugins:   https://www.gyan.dev/ffmpeg/builds/ffmpeg-frei0r-plugins
lensfun database: https://www.gyan.dev/ffmpeg/builds/ffmpeg-lensfun-db
whisper models:   https://huggingface.co/ggerganov/whisper.cpp/tree/main

git-full build configuration: 

ARCH                      x86 (generic)
big-endian                no
runtime cpu detection     yes
standalone assembly       yes
x86 assembler             nasm
MMX enabled               yes
MMXEXT enabled            yes
SSE enabled               yes
SSSE3 enabled             yes
AESNI enabled             yes
AVX enabled               yes
AVX2 enabled              yes
AVX-512 enabled           yes
AVX-512ICL enabled        yes
XOP enabled               yes
FMA3 enabled              yes
FMA4 enabled              yes
i686 features enabled     yes
CMOV is fast              yes
EBX available             yes
EBP available             yes
debug symbols             yes
strip symbols             yes
optimize for size         no
optimizations             yes
static                    yes
shared                    no
network support           yes
threading support         pthreads
safe bitstream reader     yes
texi2html enabled         no
perl enabled              yes
pod2man enabled           yes
makeinfo enabled          yes
makeinfo supports HTML    yes
experimental features     yes
xmllint enabled           yes

External libraries:
avisynth                libgsm                  libsvtav1
bzlib                   libharfbuzz             libtheora
cairo                   libilbc                 libtwolame
chromaprint             libjxl                  libuavs3d
frei0r                  liblc3                  libvidstab
gmp                     liblensfun              libvmaf
gnutls                  libmodplug              libvo_amrwbenc
iconv                   libmp3lame              libvorbis
ladspa                  libmysofa               libvpx
lcms2                   liboapv                 libvvenc
libaom                  libopencore_amrnb       libwebp
libaribb24              libopencore_amrwb       libx264
libaribcaption          libopenjpeg             libx265
libass                  libopenmpt              libxavs2
libbluray               libopus                 libxevd
libbs2b                 libplacebo              libxeve
libcaca                 libqrencode             libxml2
libcdio                 libquirc                libxvid
libcodec2               librav1e                libzimg
libdav1d                librist                 libzmq
libdavs2                librubberband           libzvbi
libdvdnav               libshaderc              lzma
libdvdread              libshine                mediafoundation
libflite                libsnappy               openal
libfontconfig           libsoxr                 sdl2
libfreetype             libspeex                whisper
libfribidi              libsrt                  zlib
libgme                  libssh

External libraries providing hardware acceleration:
amf                     d3d12va                 nvdec
cuda                    dxva2                   nvenc
cuda_llvm               ffnvcodec               opencl
cuvid                   libmfx                  vaapi
d3d11va                 libvpl                  vulkan

Libraries:
avcodec                 avformat                swscale
avdevice                avutil
avfilter                swresample

Programs:
ffmpeg                  ffplay                  ffprobe

Enabled decoders:
aac                     fmvc                    pcm_u32le
aac_fixed               fourxm                  pcm_u8
aac_latm                fraps                   pcm_vidc
aasc                    frwu                    pcx
ac3                     ftr                     pdv
ac3_fixed               g2m                     pfm
acelp_kelvin            g723_1                  pgm
adpcm_4xm               g728                    pgmyuv
adpcm_adx               g729                    pgssub
adpcm_afc               gdv                     pgx
adpcm_agm               gem                     phm
adpcm_aica              gif                     photocd
adpcm_argo              gremlin_dpcm            pictor
adpcm_circus            gsm                     pixlet
adpcm_ct                gsm_ms                  pjs
adpcm_dtk               h261                    png
adpcm_ea                h263                    ppm
adpcm_ea_maxis_xa       h263i                   prores
adpcm_ea_r1             h263p                   prores_raw
adpcm_ea_r2             h264                    prosumer
adpcm_ea_r3             h264_amf                psd
adpcm_ea_xas            h264_cuvid              ptx
adpcm_g722              h264_qsv                qcelp
adpcm_g726              hap                     qdm2
adpcm_g726le            hca                     qdmc
adpcm_ima_acorn         hcom                    qdraw
adpcm_ima_alp           hdr                     qoa
adpcm_ima_amv           hevc                    qoi
adpcm_ima_apc           hevc_amf                qpeg
adpcm_ima_apm           hevc_cuvid              qtrle
adpcm_ima_cunning       hevc_qsv                r10k
adpcm_ima_dat4          hnm4_video              r210
adpcm_ima_dk3           hq_hqa                  ra_144
adpcm_ima_dk4           hqx                     ra_288
adpcm_ima_ea_eacs       huffyuv                 ralf
adpcm_ima_ea_sead       hymt                    rasc
adpcm_ima_escape        iac                     rawvideo
adpcm_ima_hvqm2         idcin                   realtext
adpcm_ima_hvqm4         idf                     rka
adpcm_ima_iss           iff_ilbm                rl2
adpcm_ima_magix         ilbc                    roq
adpcm_ima_moflex        imc                     roq_dpcm
adpcm_ima_mtf           imm4                    rpza
adpcm_ima_oki           imm5                    rscc
adpcm_ima_pda           indeo2                  rtv1
adpcm_ima_qt            indeo3                  rv10
adpcm_ima_rad           indeo4                  rv20
adpcm_ima_smjpeg        indeo5                  rv30
adpcm_ima_ssi           interplay_acm           rv40
adpcm_ima_wav           interplay_dpcm          rv60
adpcm_ima_ws            interplay_video         s302m
adpcm_ima_xbox          ipu                     sami
adpcm_ms                jacosub                 sanm
adpcm_mtaf              jpeg2000                sbc
adpcm_n64               jpegls                  scpr
adpcm_psx               jv                      screenpresso
adpcm_psxc              kgv1                    sdx2_dpcm
adpcm_sanyo             kmvc                    sga
adpcm_sbpro_2           lagarith                sgi
adpcm_sbpro_3           lead                    sgirle
adpcm_sbpro_4           libaom_av1              sheervideo
adpcm_swf               libaribb24              shorten
adpcm_thp               libaribcaption          simbiosis_imx
adpcm_thp_le            libcodec2               sipr
adpcm_vima              libdav1d                siren
adpcm_xa                libdavs2                smackaud
adpcm_xmd               libgsm                  smacker
adpcm_yamaha            libgsm_ms               smc
adpcm_zork              libilbc                 smvjpeg
agm                     libjxl                  snow
ahx                     libjxl_anim             sol_dpcm
aic                     liblc3                  sonic
alac                    libopencore_amrnb       sp5x
alias_pix               libopencore_amrwb       speedhq
als                     libopus                 speex
amrnb                   libspeex                srgc
amrwb                   libuavs3d               srt
amv                     libvorbis               ssa
anm                     libvpx_vp8              stl
ansi                    libvpx_vp9              subrip
anull                   libxevd                 subviewer
apac                    libzvbi_teletext        subviewer1
ape                     loco                    sunrast
apng                    lscr                    svq1
aptx                    m101                    svq3
aptx_hd                 mace3                   tak
apv                     mace6                   targa
arbc                    magicyuv                targa_y216
argo                    mdec                    tdsc
ass                     media100                text
asv1                    metasound               theora
asv2                    microdvd                thp
atrac1                  mimic                   tiertexseqvideo
atrac3                  misc4                   tiff
atrac3al                mjpeg                   tmv
atrac3p                 mjpeg_cuvid             truehd
atrac3pal               mjpeg_qsv               truemotion1
atrac9                  mjpegb                  truemotion2
aura                    mlp                     truemotion2rt
aura2                   mmvideo                 truespeech
av1                     mobiclip                tscc
av1_amf                 motionpixels            tscc2
av1_cuvid               movtext                 tta
av1_qsv                 mp1                     twinvq
avrn                    mp1float                txd
avrp                    mp2                     ulti
avs                     mp2float                utvideo
avui                    mp3                     v210
bethsoftvid             mp3adu                  v210x
bfi                     mp3adufloat             v308
bink                    mp3float                v408
binkaudio_dct           mp3on4                  v410
binkaudio_rdft          mp3on4float             vb
bintext                 mpc7                    vble
bitpacked               mpc8                    vbn
bmp                     mpeg1_cuvid             vc1
bmv_audio               mpeg1video              vc1_cuvid
bmv_video               mpeg2_cuvid             vc1_qsv
bonk                    mpeg2_qsv               vc1image
brender_pix             mpeg2video              vcr1
c93                     mpeg4                   vmdaudio
cavs                    mpeg4_cuvid             vmdvideo
cbd2_dpcm               mpegvideo               vmix
ccaption                mpl2                    vmnc
cdgraphics              msa1                    vnull
cdtoons                 mscc                    vorbis
cdxl                    msmpeg4v1               vp3
cfhd                    msmpeg4v2               vp4
cinepak                 msmpeg4v3               vp5
clearvideo              msnsiren                vp6
cljr                    msp2                    vp6a
cllc                    msrle                   vp6f
comfortnoise            mss1                    vp7
cook                    mss2                    vp8
cpia                    msvideo1                vp8_cuvid
cri                     mszh                    vp8_qsv
cscd                    mts2                    vp9
cyuv                    mv30                    vp9_amf
dca                     mvc1                    vp9_cuvid
dds                     mvc2                    vp9_qsv
derf_dpcm               mvdv                    vplayer
dfa                     mvha                    vqa
dfpwm                   mwsc                    vqc
dirac                   mxpeg                   vvc
dnxhd                   nellymoser              vvc_qsv
dolby_e                 notchlc                 wady_dpcm
dpx                     nuv                     wavarc
dsd_lsbf                on2avc                  wavpack
dsd_lsbf_planar         opus                    wbmp
dsd_msbf                osq                     wcmv
dsd_msbf_planar         paf_audio               webp
dsicinaudio             paf_video               webvtt
dsicinvideo             pam                     wmalossless
dss_sp                  pbm                     wmapro
dst                     pcm_alaw                wmav1
dvaudio                 pcm_bluray              wmav2
dvbsub                  pcm_dvd                 wmavoice
dvdsub                  pcm_f16le               wmv1
dvvideo                 pcm_f24le               wmv2
dxa                     pcm_f32be               wmv3
dxtory                  pcm_f32le               wmv3image
dxv                     pcm_f64be               wnv1
eac3                    pcm_f64le               wrapped_avframe
eacmv                   pcm_lxf                 ws_snd1
eamad                   pcm_mulaw               xan_dpcm
eatgq                   pcm_s16be               xan_wc3
eatgv                   pcm_s16be_planar        xan_wc4
eatqi                   pcm_s16le               xbin
eightbps                pcm_s16le_planar        xbm
eightsvx_exp            pcm_s24be               xface
eightsvx_fib            pcm_s24daud             xl
escape124               pcm_s24le               xma1
escape130               pcm_s24le_planar        xma2
evrc                    pcm_s32be               xpm
exr                     pcm_s32le               xsub
fastaudio               pcm_s32le_planar        xwd
ffv1                    pcm_s64be               y41p
ffvhuff                 pcm_s64le               ylc
ffwavesynth             pcm_s8                  yop
fic                     pcm_s8_planar           yuv4
fits                    pcm_sga                 zero12v
flac                    pcm_u16be               zerocodec
flashsv                 pcm_u16le               zlib
flashsv2                pcm_u24be               zmbv
flic                    pcm_u24le
flv                     pcm_u32be

Enabled encoders:
a64multi                hevc_mf                 pcm_s32le
a64multi5               hevc_nvenc              pcm_s32le_planar
aac                     hevc_qsv                pcm_s64be
aac_mf                  hevc_vaapi              pcm_s64le
ac3                     hevc_vulkan             pcm_s8
ac3_fixed               huffyuv                 pcm_s8_planar
ac3_mf                  jpeg2000                pcm_u16be
adpcm_adx               jpegls                  pcm_u16le
adpcm_argo              libaom_av1              pcm_u24be
adpcm_g722              libcodec2               pcm_u24le
adpcm_g726              libgsm                  pcm_u32be
adpcm_g726le            libgsm_ms               pcm_u32le
adpcm_ima_alp           libilbc                 pcm_u8
adpcm_ima_amv           libjxl                  pcm_vidc
adpcm_ima_apm           libjxl_anim             pcx
adpcm_ima_qt            liblc3                  pfm
adpcm_ima_ssi           libmp3lame              pgm
adpcm_ima_wav           liboapv                 pgmyuv
adpcm_ima_ws            libopencore_amrnb       phm
adpcm_ms                libopenjpeg             png
adpcm_swf               libopus                 ppm
adpcm_yamaha            librav1e                prores
alac                    libshine                prores_aw
alias_pix               libspeex                prores_ks
amv                     libsvtav1               qoi
anull                   libtheora               qtrle
apng                    libtwolame              r10k
aptx                    libvo_amrwbenc          r210
aptx_hd                 libvorbis               ra_144
ass                     libvpx_vp8              rawvideo
asv1                    libvpx_vp9              roq
asv2                    libvvenc                roq_dpcm
av1_amf                 libwebp                 rpza
av1_mf                  libwebp_anim            rv10
av1_nvenc               libx264                 rv20
av1_qsv                 libx264rgb              s302m
av1_vaapi               libx265                 sbc
av1_vulkan              libxavs2                sgi
avrp                    libxeve                 smc
avui                    libxvid                 snow
bitpacked               ljpeg                   speedhq
bmp                     magicyuv                srt
cfhd                    mjpeg                   ssa
cinepak                 mjpeg_qsv               subrip
cljr                    mjpeg_vaapi             sunrast
comfortnoise            mlp                     svq1
dca                     movtext                 targa
dfpwm                   mp2                     text
dnxhd                   mp2fixed                tiff
dpx                     mp3_mf                  truehd
dvbsub                  mpeg1video              tta
dvdsub                  mpeg2_qsv               ttml
dvvideo                 mpeg2_vaapi             utvideo
dxv                     mpeg2video              v210
eac3                    mpeg4                   v308
exr                     msmpeg4v2               v408
ffv1                    msmpeg4v3               v410
ffv1_vulkan             msrle                   vbn
ffvhuff                 msvideo1                vc2
fits                    nellymoser              vnull
flac                    opus                    vorbis
flashsv                 pam                     vp8_vaapi
flashsv2                pbm                     vp9_qsv
flv                     pcm_alaw                vp9_vaapi
g723_1                  pcm_bluray              wavpack
gif                     pcm_dvd                 wbmp
h261                    pcm_f32be               webvtt
h263                    pcm_f32le               wmav1
h263p                   pcm_f64be               wmav2
h264_amf                pcm_f64le               wmv1
h264_d3d12va            pcm_mulaw               wmv2
h264_mf                 pcm_s16be               wrapped_avframe
h264_nvenc              pcm_s16be_planar        xbm
h264_qsv                pcm_s16le               xface
h264_vaapi              pcm_s16le_planar        xsub
h264_vulkan             pcm_s24be               xwd
hap                     pcm_s24daud             y41p
hdr                     pcm_s24le               yuv4
hevc_amf                pcm_s24le_planar        zlib
hevc_d3d12va            pcm_s32be               zmbv

Enabled hwaccels:
av1_d3d11va             hevc_dxva2              vc1_dxva2
av1_d3d11va2            hevc_nvdec              vc1_nvdec
av1_d3d12va             hevc_vaapi              vc1_vaapi
av1_dxva2               hevc_vulkan             vp8_nvdec
av1_nvdec               mjpeg_nvdec             vp8_vaapi
av1_vaapi               mjpeg_vaapi             vp9_d3d11va
av1_vulkan              mpeg1_nvdec             vp9_d3d11va2
dpx_vulkan              mpeg2_d3d11va           vp9_d3d12va
ffv1_vulkan             mpeg2_d3d11va2          vp9_dxva2
h263_vaapi              mpeg2_d3d12va           vp9_nvdec
h264_d3d11va            mpeg2_dxva2             vp9_vaapi
h264_d3d11va2           mpeg2_nvdec             vp9_vulkan
h264_d3d12va            mpeg2_vaapi             vvc_vaapi
h264_dxva2              mpeg4_nvdec             wmv3_d3d11va
h264_nvdec              mpeg4_vaapi             wmv3_d3d11va2
h264_vaapi              prores_raw_vulkan       wmv3_d3d12va
h264_vulkan             prores_vulkan           wmv3_dxva2
hevc_d3d11va            vc1_d3d11va             wmv3_nvdec
hevc_d3d11va2           vc1_d3d11va2            wmv3_vaapi
hevc_d3d12va            vc1_d3d12va

Enabled parsers:
aac                     dvd_nav                 mpegaudio
aac_latm                dvdsub                  mpegvideo
ac3                     evc                     opus
adx                     ffv1                    png
ahx                     flac                    pnm
amr                     ftr                     prores
apv                     g723_1                  prores_raw
av1                     g729                    qoi
avs2                    gif                     rv34
avs3                    gsm                     sbc
bmp                     h261                    sipr
cavsvideo               h263                    tak
cook                    h264                    vc1
cri                     hdr                     vorbis
dca                     hevc                    vp3
dirac                   ipu                     vp8
dnxhd                   jpeg2000                vp9
dnxuc                   jpegxl                  vvc
dolby_e                 misc4                   webp
dpx                     mjpeg                   xbm
dvaudio                 mlp                     xma
dvbsub                  mpeg4video              xwd

Enabled demuxers:
aa                      ico                     pcm_f64le
aac                     idcin                   pcm_mulaw
aax                     idf                     pcm_s16be
ac3                     iff                     pcm_s16le
ac4                     ifv                     pcm_s24be
ace                     ilbc                    pcm_s24le
acm                     image2                  pcm_s32be
act                     image2_alias_pix        pcm_s32le
adf                     image2_brender_pix      pcm_s8
adp                     image2pipe              pcm_u16be
ads                     image_bmp_pipe          pcm_u16le
adx                     image_cri_pipe          pcm_u24be
aea                     image_dds_pipe          pcm_u24le
afc                     image_dpx_pipe          pcm_u32be
aiff                    image_exr_pipe          pcm_u32le
aix                     image_gem_pipe          pcm_u8
alp                     image_gif_pipe          pcm_vidc
amr                     image_hdr_pipe          pdv
amrnb                   image_j2k_pipe          pjs
amrwb                   image_jpeg_pipe         pmp
anm                     image_jpegls_pipe       pp_bnk
apac                    image_jpegxl_pipe       pva
apc                     image_pam_pipe          pvf
ape                     image_pbm_pipe          qcp
apm                     image_pcx_pipe          qoa
apng                    image_pfm_pipe          r3d
aptx                    image_pgm_pipe          rawvideo
aptx_hd                 image_pgmyuv_pipe       rcwt
apv                     image_pgx_pipe          realtext
aqtitle                 image_phm_pipe          redspark
argo_asf                image_photocd_pipe      rka
argo_brp                image_pictor_pipe       rl2
argo_cvg                image_png_pipe          rm
asf                     image_ppm_pipe          roq
asf_o                   image_psd_pipe          rpl
ass                     image_qdraw_pipe        rsd
ast                     image_qoi_pipe          rso
au                      image_sgi_pipe          rtp
av1                     image_sunrast_pipe      rtsp
avi                     image_svg_pipe          s337m
avisynth                image_tiff_pipe         sami
avr                     image_vbn_pipe          sap
avs                     image_webp_pipe         sbc
avs2                    image_xbm_pipe          sbg
avs3                    image_xpm_pipe          scc
bethsoftvid             image_xwd_pipe          scd
bfi                     imf                     sdns
bfstm                   ingenient               sdp
bink                    ipmovie                 sdr2
binka                   ipu                     sds
bintext                 ircam                   sdx
bit                     iss                     segafilm
bitpacked               iv8                     ser
bmv                     ivf                     sga
boa                     ivr                     shorten
bonk                    jacosub                 siff
brstm                   jpegxl_anim             simbiosis_imx
c93                     jv                      sln
caf                     kux                     smacker
cavsvideo               kvag                    smjpeg
cdg                     laf                     smush
cdxl                    lc3                     sol
cine                    libgme                  sox
codec2                  libmodplug              spdif
codec2raw               libopenmpt              srt
concat                  live_flv                stl
dash                    lmlm4                   str
data                    loas                    subviewer
daud                    lrc                     subviewer1
dcstr                   luodat                  sup
derf                    lvf                     svag
dfa                     lxf                     svs
dfpwm                   m4v                     swf
dhav                    matroska                tak
dirac                   mca                     tedcaptions
dnxhd                   mcc                     thp
dsf                     mgsts                   threedostr
dsicin                  microdvd                tiertexseq
dss                     mjpeg                   tmv
dts                     mjpeg_2000              truehd
dtshd                   mlp                     tta
dv                      mlv                     tty
dvbsub                  mm                      txd
dvbtxt                  mmf                     ty
dvdvideo                mods                    usm
dxa                     moflex                  v210
ea                      mov                     v210x
ea_cdata                mp3                     vag
eac3                    mpc                     vc1
epaf                    mpc8                    vc1t
evc                     mpegps                  vividas
ffmetadata              mpegts                  vivo
filmstrip               mpegtsraw               vmd
fits                    mpegvideo               vobsub
flac                    mpjpeg                  voc
flic                    mpl2                    vpk
flv                     mpsub                   vplayer
fourxm                  msf                     vqf
frm                     msnwc_tcp               vvc
fsb                     msp                     w64
fwse                    mtaf                    wady
g722                    mtv                     wav
g723_1                  musx                    wavarc
g726                    mv                      wc3
g726le                  mvi                     webm_dash_manifest
g728                    mxf                     webvtt
g729                    mxg                     wsaud
gdv                     nc                      wsd
genh                    nistsphere              wsvqa
gif                     nsp                     wtv
gsm                     nsv                     wv
gxf                     nut                     wve
h261                    nuv                     xa
h263                    obu                     xbin
h264                    ogg                     xmd
hca                     oma                     xmv
hcom                    osq                     xvag
hevc                    paf                     xwma
hls                     pcm_alaw                yop
hnm                     pcm_f32be               yuv4mpegpipe
hxvs                    pcm_f32le
iamf                    pcm_f64be

Enabled muxers:
a64                     h261                    pcm_s16be
ac3                     h263                    pcm_s16le
ac4                     h264                    pcm_s24be
adts                    hash                    pcm_s24le
adx                     hds                     pcm_s32be
aea                     hevc                    pcm_s32le
aiff                    hls                     pcm_s8
alp                     iamf                    pcm_u16be
amr                     ico                     pcm_u16le
amv                     ilbc                    pcm_u24be
apm                     image2                  pcm_u24le
apng                    image2pipe              pcm_u32be
aptx                    ipod                    pcm_u32le
aptx_hd                 ircam                   pcm_u8
apv                     ismv                    pcm_vidc
argo_asf                ivf                     psp
argo_cvg                jacosub                 rawvideo
asf                     kvag                    rcwt
asf_stream              latm                    rm
ass                     lc3                     roq
ast                     lrc                     rso
au                      m4v                     rtp
avi                     matroska                rtp_mpegts
avif                    matroska_audio          rtsp
avm2                    mcc                     sap
avs2                    md5                     sbc
avs3                    microdvd                scc
bit                     mjpeg                   segafilm
caf                     mkvtimestamp_v2         segment
cavsvideo               mlp                     smjpeg
chromaprint             mmf                     smoothstreaming
codec2                  mov                     sox
codec2raw               mp2                     spdif
crc                     mp3                     spx
dash                    mp4                     srt
data                    mpeg1system             stream_segment
daud                    mpeg1vcd                streamhash
dfpwm                   mpeg1video              sup
dirac                   mpeg2dvd                swf
dnxhd                   mpeg2svcd               tee
dts                     mpeg2video              tg2
dv                      mpeg2vob                tgp
eac3                    mpegts                  truehd
evc                     mpjpeg                  tta
f4v                     mxf                     ttml
ffmetadata              mxf_d10                 uncodedframecrc
fifo                    mxf_opatom              vc1
filmstrip               null                    vc1t
fits                    nut                     voc
flac                    obu                     vvc
flv                     oga                     w64
framecrc                ogg                     wav
framehash               ogv                     webm
framemd5                oma                     webm_chunk
g722                    opus                    webm_dash_manifest
g723_1                  pcm_alaw                webp
g726                    pcm_f32be               webvtt
g726le                  pcm_f32le               wsaud
gif                     pcm_f64be               wtv
gsm                     pcm_f64le               wv
gxf                     pcm_mulaw               yuv4mpegpipe

Enabled protocols:
async                   http                    rtmp
bluray                  httpproxy               rtmpe
cache                   https                   rtmps
concat                  icecast                 rtmpt
concatf                 ipfs_gateway            rtmpte
crypto                  ipns_gateway            rtmpts
data                    librist                 rtp
fd                      libsrt                  srtp
ffrtmpcrypt             libssh                  subfile
ffrtmphttp              libzmq                  tcp
file                    md5                     tee
ftp                     mmsh                    tls
gopher                  mmst                    udp
gophers                 pipe                    udplite
hls                     prompeg

Enabled filters:
a3dscope                decimate                perms
aap                     deconvolve              perspective
abench                  dedot                   phase
abitscope               deesser                 photosensitivity
acompressor             deflate                 pixdesctest
acontrast               deflicker               pixelize
acopy                   deinterlace_qsv         pixscope
acrossfade              deinterlace_vaapi       pp7
acrossover              dejudder                premultiply
acrusher                delogo                  premultiply_dynamic
acue                    denoise_vaapi           prewitt
addroi                  deshake                 prewitt_opencl
adeclick                deshake_opencl          procamp_vaapi
adeclip                 despill                 program_opencl
adecorrelate            detelecine              pseudocolor
adelay                  dialoguenhance          psnr
adenorm                 dilation                pullup
aderivative             dilation_opencl         qp
adrawgraph              displace                qrencode
adrc                    doubleweave             qrencodesrc
adynamicequalizer       drawbox                 quirc
adynamicsmooth          drawbox_vaapi           random
aecho                   drawgraph               readeia608
aemphasis               drawgrid                readvitc
aeval                   drawtext                realtime
aevalsrc                drawvg                  remap
aexciter                drmeter                 remap_opencl
afade                   dynaudnorm              removegrain
afdelaysrc              earwax                  removelogo
afftdn                  ebur128                 repeatfields
afftfilt                edgedetect              replaygain
afir                    elbg                    reverse
afireqsrc               entropy                 rgbashift
afirsrc                 epx                     rgbtestsrc
aformat                 eq                      roberts
afreqshift              equalizer               roberts_opencl
afwtdn                  erosion                 rotate
agate                   erosion_opencl          rubberband
agraphmonitor           estdif                  sab
ahistogram              exposure                scale
aiir                    extractplanes           scale2ref
aintegral               extrastereo             scale_cuda
ainterleave             fade                    scale_d3d11
alatency                feedback                scale_qsv
alimiter                fftdnoiz                scale_vaapi
allpass                 fftfilt                 scale_vulkan
allrgb                  field                   scdet
allyuv                  fieldhint               scdet_vulkan
aloop                   fieldmatch              scharr
alphaextract            fieldorder              scroll
alphamerge              fillborders             segment
amerge                  find_rect               select
ametadata               firequalizer            selectivecolor
amix                    flanger                 sendcmd
amovie                  flip_vulkan             separatefields
amplify                 flite                   setdar
amultiply               floodfill               setfield
anequalizer             format                  setparams
anlmdn                  fps                     setpts
anlmf                   framepack               setrange
anlms                   framerate               setsar
anoisesrc               framestep               settb
anull                   freezedetect            sharpness_vaapi
anullsink               freezeframes            shear
anullsrc                frei0r                  showcqt
apad                    frei0r_src              showcwt
aperms                  fspp                    showfreqs
aphasemeter             fsync                   showinfo
aphaser                 gblur                   showpalette
aphaseshift             gblur_vulkan            showspatial
apsnr                   geq                     showspectrum
apsyclip                gfxcapture              showspectrumpic
apulsator               gradfun                 showvolume
arealtime               gradients               showwaves
aresample               graphmonitor            showwavespic
areverse                grayworld               shuffleframes
arls                    greyedge                shufflepixels
arnndn                  guided                  shuffleplanes
asdr                    haas                    sidechaincompress
asegment                haldclut                sidechaingate
aselect                 haldclutsrc             sidedata
asendcmd                hdcd                    sierpinski
asetnsamples            headphone               signalstats
asetpts                 hflip                   signature
asetrate                hflip_vulkan            silencedetect
asettb                  highpass                silenceremove
ashowinfo               highshelf               sinc
asidedata               hilbert                 sine
asisdr                  histeq                  siti
asoftclip               histogram               smartblur
aspectralstats          hqdn3d                  smptebars
asplit                  hqx                     smptehdbars
ass                     hstack                  sobel
astats                  hstack_qsv              sobel_opencl
astreamselect           hstack_vaapi            sofalizer
asubboost               hsvhold                 spectrumsynth
asubcut                 hsvkey                  speechnorm
asupercut               hue                     split
asuperpass              huesaturation           spp
asuperstop              hwdownload              sr_amf
atadenoise              hwmap                   ssim
atempo                  hwupload                ssim360
atilt                   hwupload_cuda           stereo3d
atrim                   hysteresis              stereotools
avectorscope            iccdetect               stereowiden
avgblur                 iccgen                  streamselect
avgblur_opencl          identity                subtitles
avgblur_vulkan          idet                    super2xsai
avsynctest              il                      superequalizer
axcorrelate             inflate                 surround
azmq                    interlace               swaprect
backgroundkey           interlace_vulkan        swapuv
bandpass                interleave              tblend
bandreject              join                    telecine
bass                    kerndeint               testsrc
bbox                    kirsch                  testsrc2
bench                   ladspa                  thistogram
bilateral               lagfun                  threshold
bilateral_cuda          latency                 thumbnail
biquad                  lenscorrection          thumbnail_cuda
bitplanenoise           lensfun                 tile
blackdetect             libplacebo              tiltandshift
blackdetect_vulkan      libvmaf                 tiltshelf
blackframe              life                    tinterlace
blend                   limitdiff               tlut2
blend_vulkan            limiter                 tmedian
blockdetect             loop                    tmidequalizer
blurdetect              loudnorm                tmix
bm3d                    lowpass                 tonemap
boxblur                 lowshelf                tonemap_opencl
boxblur_opencl          lumakey                 tonemap_vaapi
bs2b                    lut                     tpad
bwdif                   lut1d                   transpose
bwdif_cuda              lut2                    transpose_opencl
bwdif_vulkan            lut3d                   transpose_vaapi
cas                     lutrgb                  transpose_vulkan
ccrepack                lutyuv                  treble
cellauto                mandelbrot              tremolo
channelmap              maskedclamp             trim
channelsplit            maskedmax               unpremultiply
chorus                  maskedmerge             unsharp
chromaber_vulkan        maskedmin               unsharp_opencl
chromahold              maskedthreshold         untile
chromakey               maskfun                 uspp
chromakey_cuda          mcdeint                 v360
chromanr                mcompand                vaguedenoiser
chromashift             median                  varblur
ciescope                mergeplanes             vectorscope
codecview               mestimate               vflip
color                   metadata                vflip_vulkan
color_vulkan            midequalizer            vfrdet
colorbalance            minterpolate            vibrance
colorchannelmixer       mix                     vibrato
colorchart              monochrome              vidstabdetect
colorcontrast           morpho                  vidstabtransform
colorcorrect            movie                   vif
colordetect             mpdecimate              vignette
colorhold               mptestsrc               virtualbass
colorize                msad                    vmafmotion
colorkey                multiply                volume
colorkey_opencl         negate                  volumedetect
colorlevels             nlmeans                 vpp_amf
colormap                nlmeans_opencl          vpp_qsv
colormatrix             nlmeans_vulkan          vstack
colorspace              nnedi                   vstack_qsv
colorspace_cuda         noformat                vstack_vaapi
colorspectrum           noise                   w3fdif
colortemperature        normalize               waveform
compand                 null                    weave
compensationdelay       nullsink                whisper
concat                  nullsrc                 xbr
convolution             openclsrc               xcorrelate
convolution_opencl      oscilloscope            xfade
convolve                overlay                 xfade_opencl
copy                    overlay_cuda            xfade_vulkan
corr                    overlay_opencl          xmedian
cover_rect              overlay_qsv             xpsnr
crop                    overlay_vaapi           xstack
cropdetect              overlay_vulkan          xstack_qsv
crossfeed               owdenoise               xstack_vaapi
crystalizer             pad                     yadif
cue                     pad_cuda                yadif_cuda
curves                  pad_opencl              yaepblur
datascope               pad_vaapi               yuvtestsrc
dblur                   pal100bars              zmq
dcshift                 pal75bars               zoneplate
dctdnoiz                palettegen              zoompan
ddagrab                 paletteuse              zscale
deband                  pan
deblock                 perlin

Enabled bsfs:
aac_adtstoasc           h264_metadata           pgs_frame_merge
ahx_to_mp2              h264_mp4toannexb        prores_metadata
apv_metadata            h264_redundant_pps      remove_extradata
av1_frame_merge         hapqa_extract           setts
av1_frame_split         hevc_metadata           showinfo
av1_metadata            hevc_mp4toannexb        smpte436m_to_eia608
chomp                   imx_dump_header         text2movsub
dca_core                media100_to_mjpegb      trace_headers
dovi_rpu                mjpeg2jpeg              truehd_core
dts2pts                 mjpega_dump_header      vp9_metadata
dump_extradata          mov2textsub             vp9_raw_reorder
dv_error_marker         mpeg2_metadata          vp9_superframe
eac3_core               mpeg4_unpack_bframes    vp9_superframe_split
eia608_to_smpte436m     noise                   vvc_metadata
evc_frame_merge         null                    vvc_mp4toannexb
extract_extradata       opus_metadata
filter_units            pcm_rechunk

Enabled indevs:
dshow                   lavfi                   openal
gdigrab                 libcdio                 vfwcap

Enabled outdevs:
caca

git-full external libraries' versions: 

AMF v1.5.0
aom v3.13.1-129-g1ae7ce7b12
aribb24 v1.0.3-5-g5e9be27
aribcaption 1.1.1
AviSynthPlus v3.7.5-47-g26392507
bs2b 3.1.0
cairo 1.18.5
chromaprint 1.6.0
codec2 1.2.0-106-g96e8a19c
dav1d 1.5.2-13-g84792e6
davs2 1.7-1-gb41cf11
dvdnav 7.0.0
dvdread 7.0.1
ffnvcodec n13.0.19.0-2-g876af32
flite v2.2-55-g6c9f20d
freetype VER-2-14-1
frei0r v2.5.0-7-g40a50be
fribidi v1.0.16-2-gb28f43b
gsm 1.0.23
harfbuzz 12.2.0-44-g15eea57f
ladspa-sdk 1.17
lame 3.100
lc3 1.1.3
lcms2 2.16
lensfun v0.3.95-1846-g68417aa9
libass 0.17.4-16-ge60dddb
libcdio-paranoia 10.2
libgme 0.6.4
libilbc v3.0.4-346-g6adb26d4a4
libjxl v0.11-snapshot-462-g53042ec5
libopencore-amrnb 0.1.6
libopencore-amrwb 0.1.6
libplacebo v7.351.0-95-g53719e4
libsoxr 0.1.3
libssh 0.11.3
libtheora v1.2.0
libwebp v1.6.0-135-g4fc426c
openal-soft latest
openapv v0.2.0.4-4-gca288a8
openmpt libopenmpt-0.6.25-30-g414d461d0
opus v1.5.2-344-g57a2042d
qrencode 4.1.1
quirc 1.2
rav1e p20250624-1-gb7bf390
rist 0.2.12
rubberband v1.8.1
SDL release-2.32.0-139-g6ad5a966e
shaderc v2025.5-1-ge0a5092
shine 3.1.1
snappy 1.2.2
speex Speex-1.2.1-51-g0589522
srt v1.5.5-rc.0a-6-gf0368c69
SVT-AV1 v3.1.0-198-gb63784c5
twolame 0.4.0
uavs3d v1.1-47-g1fd0491
VAAPI 2.23.0.
vidstab v1.1.1-20-g4bd81e3
vmaf v3.0.0-123-g6b75f377
vo-amrwbenc 0.1.3
vorbis v1.3.7-21-g851cce99
VPL 2.15
vpx v1.15.2-143-g1ec7b38c1
vulkan-loader v1.4.335
vvenc v1.13.1-210-g983873d
whisper.cpp 1.8.2
x264 v0.165.3223
x265 4.1-212-g9e551a994
xavs2 1.4
xevd 0.5.0
xeve 0.5.1
xvid v1.3.7
zeromq 4.3.5
zimg release-3.0.6-211-gdf9c147
zvbi v0.2.44-4-g41477c9

