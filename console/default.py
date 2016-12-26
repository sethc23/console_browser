
class Console:
    
    def __init__(self,_parent,kwargs={}):
        self                                =   _parent.T.To_Sub_Classes(self,_parent)
        self.T                              =   _parent.T
        config_defaults                     =   {
                                                'notes_fpath'       :   self.T.os.getcwd() + '/logs/console_notes'
                                                ,'select_query'     :   ''
                                                ,'update_query'     :   ''
                                                ,'sort_select_by'   :   ''
                                                ,'date_format'      :   '%m/%d/%y'
                                                ,'skip_marked'      :   True
                                                ,'mark_skipped'     :   True
                                                ,'uid_col'          :   'uid'
                                                ,'url_col'          :   '_url'
                                                ,'npages_col'       :   'npages'
                                                ,'regex_fpath'      :   ''
                                                ,'val_dict'         :   {}
                                                ,'current_file'     :   ''
                                                ,'jump_uid'         :   ''

                                                ,'jump_uid'         :   ''
                                                ,'jump_uid'         :   ''
                                                ,'jump_uid'         :   ''
                                                ,'jump_uid'         :   ''
                                                ,'jump_uid'         :   ''
                                                ,'jump_uid'         :   ''


                                                }
        console_config                      =   {} if not hasattr(self.T,'console_config') else self.T['console_config']
        if type(console_config)==dict:
            config_defaults.update(             console_config)
        elif hasattr(console_config,'__dict__'):
            config_defaults.update(             console_config.__dict__)
        else:
            print(                              'Unrecognized format of "console_config":',str(console_config))
        ALL_CONFIG_PARAMS                   =   config_defaults
        self._config(                           ALL_CONFIG_PARAMS)
    
    def __update__(self,upd_dict):
        for k,v in upd_dict.iteritems():
            self.__dict__.update(               {k:v})

    def _config(self,kwargs):
        self.__update__(                        kwargs)
        locals().update(                        **self.__dict__)
        globals().update(                       **self.__dict__)
        locals().update(                        **self.T.__dict__)
        globals().update(                       **self.T.__dict__)

        assert select_query,'Missing value for "select_query":' + select_query
        assert update_query,'Missing value for "update_query":' + update_query

        df                                  =   pd.read_sql(select_query,eng)
        if sort_select_by:    df            =   df.sort_values(sort_select_by).reset_index(drop=True)
        
        # df['effective_date'] = df.effective_date.map(lambda s: None if s.__class__.__name__=='NaTType' else s.strftime('%m/%d/%y'))

        if skip_marked and os.path.exists(notes_fpath):
            print('\nskipping files marked in %s\n' % notes_fpath)
            fpath_list,idx_list             =   df[url_col_name].tolist(),[]
            with open(notes_fpath,'r') as f: 
                x                           =   f.read().split('\n')
            for l in x:
                try:
                    if l[0]=='/' and fpath_list.count(l)!=0:
                        _idx                =   fpath_list.index(l)
                        if idx_list.count(_idx)==0:
                            idx_list.append(    _idx)
                except:
                    pass
            df                              =   df[df.index.isin(idx_list)==False].reset_index(drop=True)
        if sort_select_by:    df            =   df.sort_values(sort_select_by).reset_index(drop=True)
        self.df                             =   df
        if regex_fpath:
            with open(regex_fpath,'r') as f: 
                self.regex_list             =   f.read().split('\n')
        self.T.br.window.implicitly_wait(       2)


    def run_review(self,debug=True):
        def get_ocr(pg_num):
            c                               =   ';\n'.join([
                                                        'cd /home/kali/PROJECTS/INTARCIA/scripts',
                                                        'pdftotext \
                                                            -f %(pg_num)s \
                                                            -l %(pg_num)s \
                                                            review/tmp.pdf - 2>&1' % {'pg_num':pg_num},
                                                    ])
            ocr_content                     =   ' '.join(get_ipython().getoutput(u'/usr/bin/zsh -c "' + c + '"'))
            return                              ocr_content
        def gen_and_goto_pg(file_num,pg_num=1,uid=None):
            
            if uid or jump_uid:
                jump_uid                    =   jump_uid if not uid else uid
                nf                          =   pd.read_sql(jump_query % jump_uid,eng)
                r                           =   nf.ix[0,:]
                new_file                    =   r['fpath']
            elif file_num>=len(file_list):
                print(                          "END OF FILES")
                return
            else:
                new_file                    =   file_list[file_num]
                r                           =   df.ix[file_idx_dict[new_file],:]

            if current_file!=new_file:
                print(                          'current_file: ' + current_file + ' NEQ new_file: ' + new_file)
                val_dict                    =   dict(zip(val_cols,['' for i in range(len(val_cols))]))

            printed                         =   False
            for k,v in val_dict.iteritems():
                if debug:       print(          it,r[it])
                if type(r[k])!=T.NoneType:
                    if not printed:
                        print(                  '\n')
                        printed             =   True
                    if current_file!=new_file:
                        val_dict[k]         =   r[k]
                    print(                      '\t%s: %s' % (k,r[k]))
            if printed:         print(          '\n')

            c                               =   ';\n'.join([
                                                        'cd /home/kali/PROJECTS/INTARCIA/scripts',
                                                        'pdftk %(fpath)s cat %(pg_num)s output review/tmp.pdf' \
                                                            % {'fpath':new_file,'pg_num':pg_num},
                                                        # 'curl -s %s > ./tmp.pdf' % new_file,
                                                        # 'pdftohtml -f %(pg_num)s -l %(pg_num)s -q ./tmp.pdf ./tmp.html' % {'pg_num':pg_num},
                                                    ])
            get_ipython().system(               u'/usr/bin/zsh -c "' + c + '"')
            br.open_page(                       'http://192.168.101.129/share/scripts/review/tmp.pdf')

            #
            # ATTEMPT TO CHANGE ZOOM TO 'fit-to-page'
            #
            # if not hasattr(br,'handle'):
            #     br.handle = br.window.current_window_handle
            # br.window.switch_to_window(br.handle)
            # br.window.switch_to.frame(br.execute("return frames.length;") - 1)
            # br.window.switch_to_active_element()
            # br.window.execute_script('window.viewer.zoomManager_.viewport_.fitToPage();')
            #

            ocr_content                     =   get_ocr(pg_num)
            return                              new_file,ocr_content

        locals().update(                        **self.__dict__)
        globals().update(                       **self.__dict__)
        locals().update(                        **self.T.__dict__)
        globals().update(                       **self.T.__dict__)

        idx_list                            =   df.index.astype(int).tolist()
        uid_list                            =   df[ uid_col ].astype(str).tolist()
        file_list                           =   df[ url_col ].astype(str).tolist()
        # date_list                           =   df.effective_date.astype(str).tolist()
        pgcnt_list                          =   df[ npages_col ].astype(int).tolist()
        file_idx_dict                       =   dict(zip(file_list,idx_list))
        file_uid_dict                       =   dict(zip(file_list,uid_list))
        # file_date_dict                      =   dict(zip(file_list,date_list))
        file_pgcnt_dict                     =   dict(zip(file_list,pgcnt_list))
        file_num,pg_num,qry,current_file    =   0,1,'',''
        qry_start,qry_vals                  =   "update cp_do set",[]
        jump_uid                            =   None
        current_file, OCR                   =   gen_and_goto_pg( file_num, pg_num )
        get_ipython().system(                   u'/usr/bin/zsh -c "date --iso-8601=seconds >> %s"' % notes_fpath)

        while True:

            qry                             =   ' '.join([
                                                        qry_start,
                                                        ',\n\t'.join(["%s = '%s'" % (k,v) 
                                                                     for k,v in val_dict.iteritems() if v]),
                                                        "\nwhere uid='%s';" % file_uid_dict[current_file],
                                                    ])
            res                             =   raw_input(' ')
            OPTS                            =   {

                                                'q'         : 'quit',
                                                'm'         : 'mark file (append filepath to save file)',
                                                'P'         : 'goto previous file',
                                                'N'         : 'goto next file',
                                                'p'         : 'goto previous page in file',
                                                'n'         : 'goto next page in file',
                                                'f'         : 'goto first page of file',
                                                'e'         : 'goto last page of file',
                                                '?'         : 'show info about file and update query',
                                                'o'         : 'print OCR of file',
                                                'D'         : 'execute update query and goto next file',
                                                 
                                                're [str]'  : 'test,save,edit,remove regex queries re: OCR text',
                                                '! [str]'   : 'execute ipython command in this namespace',
                                                'j [int]'   : 'jump to file having input uid',

                                                }
                                                #
                                                # ? CREATE FUNCTION FOR CUSTOMIZING SHORT-HANDS ON-THE-GO ?
                                                #   list
                                                #   new
                                                #   edit
                                                #   del
                                                #
                                                # 't [str]'   : 'set contract type',
                                                # 'd [str]'   : 'set contract department',
                                                # 's [str]'   : 'set contract status',
                                                # 'n [str]'   : 'set contract title',
                                                # 'd [str]'   : 'set effective date',
                                                # 'v [str]'   : 'set vendor name',
                                                # 'a [str]'   : 'set address',
                                                # 'x [str]'   : 'set expiration',
                                                # 'r [str]'   : 'set requestor',
                                                # 'i [str]'   : 'append/set notes',

            if   len(res)==0:   pass
            elif len(res)==1:
                if   res=='q':  break
                elif res=='m':
                    with open(notes_fpath,'a') as f:        f.write(current_file+'\n')
                    if debug:   print(          'marked '+notes_fpath)
                elif res=='P':
                    jump_uid                =   None
                    pg_num                  =   1
                    file_num               -=   1
                    current_file, OCR       =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='N':
                    if mark_skipped:
                        with open(notes_fpath,'a') as f:    f.write(current_file+'\n')
                    jump_uid                =   None
                    pg_num                  =   1
                    file_num               +=   1
                    current_file, OCR       =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='p':
                    pg_num                 -=   1
                    current_file, OCR       =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='n':
                    last_pg_num             =   file_pgcnt_dict[current_file]
                    if pg_num+1 > last_pg_num:
                        print(                  'already at last page')
                    else:
                        pg_num             +=   1
                        current_file, OCR   =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='e':
                    last_pg_num             =   file_pgcnt_dict[current_file]
                    if pg_num >= last_pg_num:
                        print(                  'already at last page')
                    else:
                        pg_num              =   last_pg_num
                        current_file, OCR   =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='f':
                    pg_num                  =   1
                    current_file, OCR       =   gen_and_goto_pg( file_num, pg_num )
                    if debug:   print(          current_file,pg_num)
                elif res=='?':
                    print(                      ' ')
                    # print(                      '\tcurrent_file (#%s of %s): %s' % (str(file_num)
                    #                             ,str(len(file_list))
                    #                             ,str(current_file.replace('/home/kali/PROJECTS/INTARCIA/',''))))
                    # print(                      '\tpg_num: '+str(pg_num))
                    # print(                      '\ttotal_pages: '+str(file_pgcnt_dict[current_file]))
                    # print(                      ' ')
                    # for k,v in val_dict.iteritems():
                    #     if v:
                    #         print               'v: ',v
                    #         if   k=='contract_type':
                    #             v           =   c_type_dict[k]
                    #         elif k=='contract_dept':
                    #             v           =   c_dept_dict[k]
                    #         elif k=='contract_status':
                    #             v           =   c_status_dict[k]
                    #         print               '%s:\t%s' % (k,str(v))
                    print(                      ' ')                
                elif res=='o':  print(          OCR)
                elif res=='D':
                    if debug:   print(          qry)
                    else:
                        try:
                            print               qry
                            to_sql(             qry)
                            print(              'DB updated')
                            val_dict        =   dict(zip(val_cols,['' for i in range(len(val_cols))]))
                            jump_uid        =   None
                            file_num       +=   1
                            pg_num          =   1
                            current_file, OCR=  gen_and_goto_pg( file_num, pg_num )
                        except:
                            print(              '\nQRY FAILED: %s\n' % qry)
                        
            elif res[:3]=='re ':
                """
                    test single
                    test all
                    append regex
                    edit regex

                """
                print(                          ' ')
                r                           =   res[3:]
                if   r    =='?':
                    for it in regex_list:
                        print(                  re.search(r'%s' % it,OCR))
                elif r[:2]=='l ':
                    pt                      =   0
                    for it in regex_list:
                        print(                  '%s: %s' % (str(pt),it))
                        pt                 +=   1
                elif r[:2]=='a ':
                    _regex                  =   r[2:]
                    regex_list.append(          _regex)
                    with open(regex_fpath,'w') as f:        f.write('\n'.join(regex_list))
                    print(                      'regex appended')
                elif r[:2]=='d ':
                    _idx                    =   int(r[2:])
                    z                       =   regex_list.pop(_idx)
                    with open(regex_fpath,'w') as f:        f.write('\n'.join(regex_list))
                    print(                      'dropped regex: %s' % z)
                elif r[:2]=='t ':
                    _regex                  =   r[2:]
                    print(                      re.search(r'%s' % _regex,OCR))

            elif res[0]=='!':
                print                           '\n'
                exec res[1:] in globals(),locals()
                print                           '\n'

            elif res[1]==' ':
                _val                        =   res[2:]
                # if   res[0]=='t':               val_dict['contract_type']   = _val
                # elif res[0]=='g':               val_dict['contract_dept']   = _val
                # elif res[0]=='s':               val_dict['contract_status'] = _val
                # elif res[0]=='n':               val_dict['contract_title']  = _val
                # elif res[0]=='d':               val_dict['effective_date']  = _val
                # elif res[0]=='v':               val_dict['vendor_name']     = _val
                # elif res[0]=='a':               val_dict['address']         = _val
                # elif res[0]=='x':               val_dict['expiration']      = _val
                # elif res[0]=='r':               val_dict['requestor']       = _val

                if   res[0]=='j':
                    jump_uid                =   _val
                    current_file, OCR       =   gen_and_goto_pg( file_num, pg_num, uid=jump_uid )

                elif res[0]=='i':
                    val_dict['notes']       =   _val if not val_dict['notes'] else val_dict['notes'] + '; ' + _val

            if debug:           print           qry

