from project_creation_tools import iso9660_project,AudioCdProject
from xml.dom.minidom import *

class ConfigSerializer:

    init_doc = '''
    <BubbleDisk version='0.1'>
    </BubbleDisk>
    '''

    def serialize (self,burning_project):
        if isinstance(burning_project,iso9660_project) :
            return self.__serialize_data_project(burning_project)
        elif isinstance(burning_project,AudioCdProject):
            return self.__serialize_audio_project(burning_project)

    def unserialize (self):
        pass

    def __serialize_data_project (self,burning_project):
        doc = parseString(self.init_doc)
        elem = doc.createElement("dataProject")
        doc.firstChild.appendChild(elem)

        elem_tmp = doc.createElement ("currentDir")
        text = doc.createTextNode (burning_project.current_dir)
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("currentSize")
        text = doc.createTextNode (str(burning_project.current_size))
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("oversized")
        text = doc.createTextNode (str(burning_project.oversized))
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("numtracks")
        text = doc.createTextNode (str(burning_project.numtracks))
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("name")
        text = doc.createTextNode (burning_project.name)
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("fileSystem")
        text = doc.createTextNode (str(burning_project.file_system))
        elem_tmp.appendChild(text)
        elem.appendChild(elem_tmp)

        mkisofsElem = doc.createElement ("mkisofs")
        elem.appendChild(mkisofsElem)

        mkisofs = burning_project.iso9660_tool

        elem_tmp = doc.createElement ("applicationId")
        text = doc.createTextNode (str(mkisofs.application_id))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("allowLeadingDots")
        text = doc.createTextNode (str(mkisofs.allow_leading_dots))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("allowLowercase")
        text = doc.createTextNode (str(mkisofs.allow_lowercase))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("allowMultidot")
        text = doc.createTextNode (str(mkisofs.allow_multidot))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("biblio")
        text = doc.createTextNode (mkisofs.biblio)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("copyright")
        text = doc.createTextNode (mkisofs.copyright)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("omitTrailingPeriod")
        text = doc.createTextNode (str(mkisofs.omit_trailing_period))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("inputCharset")
        text = doc.createTextNode (mkisofs.input_charset)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("isoLevel")
        text = doc.createTextNode (mkisofs.iso_level)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("genJoliet")
        text = doc.createTextNode (str(mkisofs.gen_joliet))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("jolietLong")
        text = doc.createTextNode (str(mkisofs.joliet_long))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("allow31CharFn")
        text = doc.createTextNode (str(mkisofs.allow_31_char_fn))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("maxIso9660Filenames")
        text = doc.createTextNode (str(mkisofs.max_iso9660_filenames))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("omitVersionNumber")
        text = doc.createTextNode (str(mkisofs.omit_version_number))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("noBak")
        text = doc.createTextNode (str(mkisofs.no_bak))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("publisher")
        text = doc.createTextNode (mkisofs.publisher)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("preparer")
        text = doc.createTextNode (mkisofs.preparer)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("genRockridgeExt")
        text = doc.createTextNode (str(mkisofs.gen_rock_ridge_ext))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("relaxedFilenames")
        text = doc.createTextNode (str(mkisofs.relaxed_filenames))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("sysid")
        text = doc.createTextNode (mkisofs.sysid)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("genTransbl")
        text = doc.createTextNode (str(mkisofs.gen_transbl))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("hideJolietTransTbl")
        text = doc.createTextNode (str(mkisofs.hide_joliet_trans_tbl))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("udf")
        text = doc.createTextNode (str(mkisofs.udf))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("allowUntranslatedFilenames")
        text = doc.createTextNode (str(mkisofs.allow_untranslated_filenames))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("noIsoTranslate")
        text = doc.createTextNode (str(mkisofs.no_iso_translate))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("volume_id")
        text = doc.createTextNode (mkisofs.volume_id)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("volset")
        text = doc.createTextNode (mkisofs.volume_id)
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("lastSessStart")
        text = doc.createTextNode (str(mkisofs.last_sess_start))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("nextSessStart")
        text = doc.createTextNode (str(mkisofs.next_sess_start))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("multisess")
        text = doc.createTextNode (str(mkisofs.multisess))
        elem_tmp.appendChild(text)
        mkisofsElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("files")
        elem.appendChild(elem_tmp)
        elem_tmp.appendChild(burning_project.vfs.doc.firstChild.cloneNode(1000))

        cdrecordElem = doc.createElement ("cdrecord")
        elem.appendChild(cdrecordElem)

        cdrecord = burning_project.burning_tool

        elem_tmp = doc.createElement ("multisess")
        text = doc.createTextNode (cdrecord.multisess)
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("trackMode")
        text = doc.createTextNode (str(cdrecord.track_mode))
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("fixating")
        text = doc.createTextNode (str(cdrecord.fixating))
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("simulation")
        text = doc.createTextNode (str(cdrecord.simulation))
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("write")
        text = doc.createTextNode (str(cdrecord.write))
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("writeMethod")
        text = doc.createTextNode (cdrecord.write_method)
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        elem_tmp = doc.createElement ("write_speed")
        text = doc.createTextNode (cdrecord.write_speed)
        elem_tmp.appendChild(text)
        cdrecordElem.appendChild(elem_tmp)

        doc_as_string = doc.toprettyxml(indent='\t',newl='\n')
        return doc_as_string

    def __serialize_audio_project (self):
        pass

