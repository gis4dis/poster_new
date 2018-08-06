from apps.importing.models import ProviderLog
from datetime import datetime

def import_provider_logs(provider):
    received_time = datetime(2018, 3, 23, 10, 30, 00)
    ProviderLog.objects.create(
        provider=provider,
        is_valid=True,
        content_type='text/xml',
        body= '''<?xml version="1.0" encoding="UTF-8"?>
                    <DOC version="3.0" id="6ad9ca25-aef4-43f4-8cb2-a14f4323cbc9" country="CZ" DataSet="extended">
                    <INF sender="JSDI_NDIC" receiver="MUNI" transmission="HTTP">
                        <DAT>
                            <EVTT version="2.01" language="CZ" />
                            <SNET type="GN" version="17.06" country="CZ" />
                            <UIRADR structure="4.2" version="1020" />
                        </DAT>
                    </INF>
                    <MJD count="1">
                        <MSG id="6f17839b-9ffe-4cfd-9b56-87346778841d" version="1" type="TI" planned="true">
                            <MTIME format="YYYY-MM-DDThh:mm:ssTZD">
                                <TGEN>2018-03-23T10:30:01+01:00</TGEN>
                                <TSTA>2018-03-26T00:00:00+02:00</TSTA>
                                <TSTO>2018-05-25T00:00:00+02:00</TSTO>
                            </MTIME>
                            <MTXT language="CZ">silnice II/386 (ulice Veveří), Ostrovačice, okr. Brno-venkov, Od 26.03.2018 00:00, Do 25.05.2018 00:00, Jedná se o úplnou uzavírku provozu na silnici č. II/386 Lipůvka-Kuřim-Veverská Bitýška-Ostrovačice v km cca od 21,030 (křižovatka se silnicí č. II/602) po 21,239 (křižovatka nájezdová rampa MÚK Ostrovačice D1 pro směr na Brno) staničení pasportu silnice, z důvodu rekonstrukce povrchu komunikace č. II/386 v obci Ostrovačice – akce „Sil. II/602 Ostrovačice – průtah 2. stavba Etapa III.A a III.B“ v termínu od 26.3.2018 do 25.52018.  

                    Dále se jedná o částečnou uzavírku provozu na silnici č. II/386 Lipůvka-Kuřim-Veverská Bitýška-Ostrovačice v úseku od rampy MÚK Ostrovačice D1 pro směr na Brno po odbočku do areálu firmy Jerex a.s., odštěpný závod Veveří 210, 664 81 Ostrovačice v termínu od 21.05.2018 do 25.5.2018. Objížďka - pro autobusovou dopravu: silnice III/3867, Veverské Knínice - ulice Višňová, Říčany, okr. Brno-venkov, přes: místní komunikace (Říčany), Objížďka - bez rozlišení: silnice II/602 (ulice Brněnská), Říčany, okr. Brno-venkov - silnice II/384, Brno-Bystrc, Brno, přes: Popůvky, místní komunikace (Brno), Vydal: Městský úřad Rosice</MTXT>
                            <MEVT>
                                <TMCE urgencyvalue="U" directionalityvalue="2" timescalevalue="L" diversion="true">
                                <EVI eventcode="401" updateclass="5" eventorder="1">
                                    <TXUCL language="CZ">Dopravní uzavírky a omezení</TXUCL>
                                    <TXEVC language="CZ">uzavřeno</TXEVC>
                                </EVI>
                                <EVI eventcode="704" updateclass="11" eventorder="2">
                                    <TXUCL language="CZ">Práce na silnici</TXUCL>
                                    <TXEVC language="CZ">oprava povrchu vozovky</TXEVC>
                                </EVI>
                                <DIV diversioncode="4" diversiontext="objížďka" language="CZ" />
                                <TXTMCE language="CZ">uzavřeno oprava povrchu vozovky</TXTMCE>
                                </TMCE>
                                <OTXT>Jedná se o úplnou uzavírku provozu na silnici č. II/386 Lipůvka-Kuřim-Veverská Bitýška-Ostrovačice v km cca od 21,030 (křižovatka se silnicí č. II/602) po 21,239 (křižovatka nájezdová rampa MÚK Ostrovačice D1 pro směr na Brno) staničení pasportu silnice, z důvodu rekonstrukce povrchu komunikace č. II/386 v obci Ostrovačice – akce „Sil. II/602 Ostrovačice – průtah 2. stavba Etapa III.A a III.B“ v termínu od 26.3.2018 do 25.52018.  

                    Dále se jedná o částečnou uzavírku provozu na silnici č. II/386 Lipůvka-Kuřim-Veverská Bitýška-Ostrovačice v úseku od rampy MÚK Ostrovačice D1 pro směr na Brno po odbočku do areálu firmy Jerex a.s., odštěpný závod Veveří 210, 664 81 Ostrovačice v termínu od 21.05.2018 do 25.5.2018.</OTXT>
                            </MEVT>
                            <MLOC>
                                <TXPL>silnice II/386 (ulice Veveří), Ostrovačice, okr. Brno-venkov</TXPL>
                                <SNTL coordsystem="WGS-84" count="4">
                                <COORD x="49.2126514120518" y="16.4071057145663" />
                                <STEL el_code="2985754" />
                                <STEL el_code="2985757" />
                                <STEL el_code="624007" />
                                <STEL el_code="1558716" />
                                </SNTL>
                            </MLOC>
                            <MDST>
                                <DEST CountryName="Česká republika" RegionCode="116" RegionName="Jihomoravský kraj" TownShipCode="3703" TownShip="Brno-venkov" TownCode="583600" TownName="Ostrovačice">
                                <STRE StreetCode="41955" StreetName="Veveří" />
                                <ROAD RoadNumber="386" RoadClass="2" />
                                </DEST>
                            </MDST>
                            <DIVLOC>
                                <DIVROUTE description="pro autobusovou dopravu" />
                                <DIVROUTE description="bez rozlišení" />
                            </DIVLOC>
                        </MSG>
                    </MJD>
                    </DOC>''',
        file_name='abc',
        file_path='/opt/poster-app/import/rsd/2018/03/20180323-093033_valid_abc_4fd9d424-a081-463f-8e90-351737e033b5.txt',
        ext='txt',
        received_time=received_time,
        uuid4='d85a4f5a-fd7f-4f62-9d76-f8ebd4c86a10',
        last_processed=None,
        # created=models.DateTimeField(auto_now_add=True)
        # updated=models.DateTimeField(auto_now=True)
    )
    return True