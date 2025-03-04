""" rule operations
"""
import logging

import irods.exception
import irods.rule

from ibridges.irodsconnector import session


class Rules(object):
    """Irods Rule operations """

    def __init__(self, session: session.Session):
        """ iRODS data operations initialization

            Parameters
            ----------
            sess_man : session.Session
                instance of the Session class

        """
        self.session = session

    def execute_rule(self, rule_file: str, params: dict, output: str = 'ruleExecOut') -> tuple:
        """Execute an iRODS rule.

        Parameters
        ----------
        rule_file : str, file-like
            Name of the iRODS rule file, or a file-like object representing it.
        params : dict
            Rule arguments.
        output : str
            Rule output variable(s).

        Returns
        -------
        tuple
            (stdout, stderr)

        `params` format example:
        params = {  # extra quotes for string literals
            '*obj': '"/zone/home/user"',
            '*name': '"attr_name"',
            '*value': '"attr_value"'
        }

        """
        try:
            rule = irods.rule.Rule(
                self.session.irods_session, rule_file=rule_file, params=params, output=output,
                instance_name='irods_rule_engine_plugin-irods_rule_language-instance')
            out = rule.execute()
        except irods.exception.NetworkException as error:
            logging.info('Lost connection to iRODS server.')
            return '', repr(error)
        except irods.exception.SYS_HEADER_READ_LEN_ERR as error:
            logging.info('iRODS server hiccuped.  Check the results and try again.')
            return '', repr(error)
        except Exception as error:
            logging.info('RULE EXECUTION ERROR', exc_info=True)
            return '', repr(error)
        stdout, stderr = '', ''
        if len(out.MsParam_PI) > 0:
            buffers = out.MsParam_PI[0].inOutStruct
            stdout = (buffers.stdoutBuf.buf or b'').decode()
            # Remove garbage after terminal newline.
            stdout = '\n'.join(stdout.split('\n')[:-1])
            stderr = (buffers.stderrBuf.buf or b'').decode()
        return stdout, stderr
