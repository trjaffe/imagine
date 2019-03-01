import unittest
import numpy as np
from nifty5 import Field, UnstructuredDomain, RGSpace, HPSpace, DomainTuple
from imagine.observables.observable import Observable
from imagine.observables.observable_dict import Simulations, Measurements, Covariances
from imagine.likelihoods.likelihood import Likelihood
from imagine.likelihoods.simple_likelihood import SimpleLikelihood
from imagine.likelihoods.ensemble_likelihood import EnsembleLikelihood
from imagine.tools.covariance_estimator import oas_mcov


class TestSimpleLikeli(unittest.TestCase):

    def test_without_cov(self):
        simdict = Simulations()
        meadict = Measurements()
        # mock measurements
        dtuple = DomainTuple.make((RGSpace(1), HPSpace(nside=2)))
        arr_a = np.random.rand(48)
        mea = Observable(dtuple, arr_a)
        meadict.append(('test', 'nan', '2', 'nan'), mea)
        # mock sims
        dtuple = DomainTuple.make((RGSpace(3), HPSpace(nside=2)))
        arr_b = np.random.rand(3, 48)
        sim = Observable(dtuple, arr_b)
        simdict.append(('test', 'nan', '2', 'nan'), sim)
        # no covariance
        lh = SimpleLikelihood(meadict)
        # calc by likelihood
        rslt = lh(simdict)
        # calc by hand
        diff = (np.mean(arr_b, axis=0) - arr_a)
        baseline = -float(0.5)*float(np.vdot(diff, diff))
        # comapre
        self.assertEqual(rslt, baseline)
    
    def test_with_cov(self):
        simdict = Simulations()
        meadict = Measurements()
        covdict = Covariances()
        # mock measurements
        dtuple = DomainTuple.make((RGSpace(1), RGSpace(12)))
        arr_a = np.random.rand(12)
        mea = Observable(dtuple, arr_a)
        meadict.append(('test', 'nan', '12', 'nan'), mea, True)
        # mock sims
        dtuple = DomainTuple.make((RGSpace(5), RGSpace(12)))
        arr_b = np.random.rand(5, 12)
        sim = Observable(dtuple, arr_b)
        simdict.append(('test', 'nan', '12', 'nan'), sim, True)
        # mock covariance
        arr_c = np.random.rand(12, 12)
        dtuple = DomainTuple.make((RGSpace(shape=arr_c.shape)))
        cov = Field.from_global_data(dtuple, arr_c)
        covdict.append(('test', 'nan', '12', 'nan'), cov, True)
        # with covariance
        lh = SimpleLikelihood(meadict, covdict)
        # calc by likelihood
        rslt = lh(simdict)
        # calc by hand
        diff = (np.mean(arr_b, axis=0) - arr_a)
        sign, logdet = np.linalg.slogdet(arr_c*2.*np.pi)
        baseline = -float(0.5)*float(np.vdot(diff, np.linalg.solve(arr_c, diff))+sign*logdet)
        self.assertEqual(rslt, baseline)


class TestEnsembleLikeli(unittest.TestCase):

    def test_oas(self):
        # mock observable
        arr_a = np.random.rand(4)
        arr_ens = np.zeros((3, 4))
        null_cov = np.zeros((4, 4))
        # ensemble with identical realisations
        for i in range(len(arr_ens)):
            arr_ens[i] = arr_a
        dtuple = DomainTuple.make((RGSpace(3), RGSpace(4)))
        obs = Observable(dtuple, arr_ens)
        test_mean, test_cov = oas_mcov(obs)
        for i in range(len(arr_a)):
            self.assertAlmostEqual(test_mean[0][i], arr_a[i])
            for j in range(len(arr_a)):
                self.assertAlmostEqual(test_cov[i][j], null_cov[i][j])
    
    def test_without_simcov(self):
        simdict = Simulations()
        meadict = Measurements()
        covdict = Covariances()
        # mock measurements
        dtuple = DomainTuple.make((RGSpace(1), HPSpace(nside=2)))
        arr_a = np.random.rand(48)
        mea = Observable(dtuple, arr_a)
        meadict.append(('test', 'nan', '2', 'nan'), mea)
        # mock covariance
        dtuple = DomainTuple.make((RGSpace(shape=(48, 48))))
        arr_c = np.random.rand(48, 48)
        cov = Field.from_global_data(dtuple, arr_c)
        covdict.append(('test', 'nan', '2', 'nan'), cov)
        # mock observable with repeated single realisation
        dtuple = DomainTuple.make((RGSpace(5), HPSpace(nside=2)))
        arr_b = np.random.rand(48) 
        arr_ens = np.zeros((5, 48))
        for i in range(len(arr_ens)):
            arr_ens[i] = arr_b
        sim = Observable(dtuple, arr_ens)
        simdict.append(('test', 'nan', '2', 'nan'), sim)
        # simplelikelihood
        lh_simple = SimpleLikelihood(meadict, covdict)
        rslt_simple = lh_simple(simdict)
        # ensemblelikelihood
        lh_ensemble = EnsembleLikelihood(meadict, covdict)
        rslt_ensemble = lh_ensemble(simdict)
        self.assertEqual(rslt_ensemble, rslt_simple)

    def test_without_cov(self):
        simdict = Simulations()
        meadict = Measurements()
        # mock measurements
        dtuple = DomainTuple.make((RGSpace(1), HPSpace(nside=2)))
        arr_a = np.random.rand(48)
        mea = Observable(dtuple, arr_a)
        meadict.append(('test', 'nan', '2', 'nan'), mea)
        # mock observable with repeated single realisation
        dtuple = DomainTuple.make((RGSpace(5), HPSpace(nside=2)))
        arr_b = np.random.rand(48)
        arr_ens = np.zeros((5, 48))
        for i in range(len(arr_ens)):
            arr_ens[i] = arr_b
        sim = Observable(dtuple, arr_ens)
        simdict.append(('test', 'nan', '2', 'nan'), sim)
        # simplelikelihood
        lh_simple = SimpleLikelihood(meadict)
        rslt_simple = lh_simple(simdict)
        # ensemblelikelihood
        lh_ensemble = EnsembleLikelihood(meadict)
        rslt_ensemble = lh_ensemble(simdict)
        self.assertEqual(rslt_ensemble, rslt_simple)


if __name__ == '__main__':
    unittest.main()
