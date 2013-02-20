# -*- coding: utf-8 -*-
from django.test import TestCase
from django.contrib.gis.geos import LineString

from caminae.core.factories import PathFactory, TopologyFactory
from caminae.core.models import Path





class SplitPathTest(TestCase):
    def test_split_tee_1(self):
        """
               C
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        self.assertEqual(ab.length, 4)
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        self.assertEqual(cd.length, 2)
        
        # Make sure AB was split :
        ab.reload()
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(ab.length, 2)  # Length was also updated
        # And a clone of AB was created
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        self.assertEqual(len(clones), 1)
        ab_2 = clones[0]
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(ab_2.length, 2)  # Length was also updated

    def test_split_tee_2(self):
        """
        CD exists. Add AB.
        """
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        self.assertEqual(cd.length, 2)
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        
        # Make sure AB was split :
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(ab.length, 2)  # Length was also updated
        
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        ab_2 = clones[0]
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(ab_2.length, 2)  # Length was also updated

    def test_split_cross(self):
        """
               C
               +
               |
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D      
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((2,-2,0),(2,2,0)))
        ab.reload()
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab.geom, LineString((0,0,0),(2,0,0)))
        self.assertEqual(cd.geom, LineString((2,-2,0),(2,0,0)))
        self.assertEqual(ab_2.geom, LineString((2,0,0),(4,0,0)))
        self.assertEqual(cd_2.geom, LineString((2,0,0),(2,2,0)))

    def test_split_cross_on_deleted(self):
        """
        Paths should not be splitted if they cross deleted paths.
        (attribute delete=True)
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        self.assertEqual(len(Path.objects.all()), 1)
        ab.delete()
        self.assertEqual(len(Path.objects.all()), 0)
        cd = PathFactory.create(name="CD", geom=LineString((2,-2,0),(2,2,0)))
        self.assertEqual(len(Path.objects.all()), 1)

    def test_split_on_update(self):
        """
                                       + E
                                       :
        A +----+----+ B         A +----+----+ B
                                       :
        C +----+ D              C +----+ D
        
                                    AB and CD exist. CD updated into CE.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,-2,0),(2,-2,0)))
        self.assertEqual(ab.length, 4)
        self.assertEqual(cd.length, 2)
        
        cd.geom = LineString((0,-2,0),(2,-2,0), (2,2,0))
        cd.save()
        ab.reload()
        self.assertEqual(ab.length, 2)
        self.assertEqual(cd.length, 4)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab_2.length, 2)
        self.assertEqual(cd_2.length, 2)

    def test_split_twice(self):
        """
        
             C   D
             +   +
             |   |
        A +--+---+--+ B
             |   |
             +---+ 
        
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((1,2,0),(1,-2,0),
                                                           (3,-2,0),(3,2,0)))
        ab.reload()
        self.assertEqual(ab.length, 1)
        self.assertEqual(cd.length, 2)
        ab_clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        cd_clones = Path.objects.filter(name="CD").exclude(pk=cd.pk)
        self.assertEqual(len(ab_clones), 2)
        self.assertEqual(len(cd_clones), 2)
        self.assertEqual(ab_clones[0].geom, LineString((1,0,0),(3,0,0)))
        self.assertEqual(ab_clones[1].geom, LineString((3,0,0),(4,0,0)))
        
        self.assertEqual(cd_clones[0].geom, LineString((1,0,0),(1,-2,0),
                                                       (3,-2,0),(3,0,0)))
        self.assertEqual(cd_clones[1].geom, LineString((3,0,0),(3,2,0)))

    def test_split_multiple(self):
        """
        
             C   E   G   I
             +   +   +   +
             |   |   |   |
        A +--+---+----------+ B
             |   |   |   |
             +   +   +   +
             D   F   H   J
        """
        PathFactory.create(name="CD", geom=LineString((1,-2,0),(1,2,0)))
        PathFactory.create(name="EF", geom=LineString((2,-2,0),(2,2,0)))
        PathFactory.create(name="GH", geom=LineString((3,-2,0),(3,2,0)))
        PathFactory.create(name="IJ", geom=LineString((4,-2,0),(4,2,0)))
        PathFactory.create(name="AB", geom=LineString((0,0,0),(5,0,0)))
        self.assertEqual(len(Path.objects.filter(name="AB")), 5)
        self.assertEqual(len(Path.objects.filter(name="CD")), 2)
        self.assertEqual(len(Path.objects.filter(name="EF")), 2)
        self.assertEqual(len(Path.objects.filter(name="GH")), 2)
        self.assertEqual(len(Path.objects.filter(name="IJ")), 2)

    def failing_test_split_multiple_2(self):
        """
              C              D
               +            +
             E  \          /  F
        A +---+--+--------+--+---+ B
               \  \      /  /            AB exists. Create EF. Create CD.
                \  \    /  /
                 +--+--+--+ 
                     \/
        """
        PathFactory.create(name="AB", geom=LineString((0,0,0),(10,0,0)))
        PathFactory.create(name="EF", geom=LineString((2,0,0),(2,-1,0),(6,-1,0),(6,0,0)))
        
        PathFactory.create(name="CD", geom=LineString((4,1,0),(5,-2,0),(6,1,0)))
        
        self.assertEqual(len(Path.objects.filter(name="AB")), 5)
        self.assertEqual(len(Path.objects.filter(name="EF")), 5)
        self.assertEqual(len(Path.objects.filter(name="CD")), 5)


class SplitPathLineTopologyTest(TestCase):

    def test_split_tee_1(self):
        """
                 C
        A +---===+===---+ B
             A'  |  B'
                 +      AB exists with topology A'B'.
                 D      Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.25, end=0.75)
        topogeom = topology.geom
        # Topology covers 1 path
        self.assertEqual(len(topology.paths.all()), 1)
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        # Topology now covers 2 paths
        self.assertEqual(len(topology.paths.all()), 2)
        # AB and AB2 has one topology each
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        # Topology position became proportional
        aggr_ab = ab.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((0.5, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.5), (aggr_cb.start_position, aggr_cb.end_position))
        topology.reload()
        self.assertNotEqual(topology.geom, topogeom)
        self.assertEqual(topology.geom.coords[0], topogeom.coords[0])
        self.assertEqual(topology.geom.coords[-1], topogeom.coords[-1])

    def test_split_tee_2(self):
        """
              C
        A +---+---=====--+ B
              |   A'  B'
              +           AB exists with topology A'B'.
              D           Add CD
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.5, end=0.75)
        topogeom = topology.geom
        # Topology covers 1 path
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.paths.all()[0], ab)
        cd = PathFactory.create(geom=LineString((1,0,0),(1,2,0)))
        # CB was just created
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        
        # AB has no topology anymore
        self.assertEqual(len(ab.aggregations.all()), 0)
        # Topology now still covers 1 path, but the new one
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(topology.paths.all()[0].pk, cb.pk)
        topology.reload()
        self.assertEqual(topology.geom, topogeom)

    def test_split_tee_3(self):
        """
                    C
        A +--=====--+---+ B
             A'  B' |   
                    +    AB exists with topology A'B'.
                    D    Add CD
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.3, end=0.6)
        topogeom = topology.geom
        # Topology covers 1 path
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(topology.paths.all()[0], ab)
        cd = PathFactory.create(geom=LineString((3,0,0),(3,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        
        # CB does not have any
        self.assertEqual(len(cb.aggregations.all()), 0)
        
        # AB has still its topology
        self.assertEqual(len(ab.aggregations.all()), 1)
        # But start/end have changed
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.4, 0.8), (aggr_ab.start_position, aggr_ab.end_position))
        topology.reload()
        self.assertEqual(topology.geom, topogeom)

    def test_split_tee_4(self):
        """
                B   C   E
        A +--===+===+===+===--+ F
                    |   
                    +    AB, BE, EF exist. A topology exists along them.
                    D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(2,0,0)))
        be = PathFactory.create(name="BE", geom=LineString((2,0,0),(4,0,0)))
        ef = PathFactory.create(name="EF", geom=LineString((4,0,0),(6,0,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.5, end=1)
        topology.add_path(be, start=0, end=1)
        topology.add_path(ef, start=0.0, end=0.5)
        topogeom = topology.geom
        
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(be.aggregations.all()), 1)
        self.assertEqual(len(ef.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 3)
        # Create CD
        cd = PathFactory.create(geom=LineString((3,0,0),(3,2,0)))
        # Topology now covers 4 paths
        self.assertEqual(len(topology.paths.all()), 4)
        # AB and EF have still their topology
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(ef.aggregations.all()), 1)
        
        # BE and CE have one topology from 0.0 to 1.0
        bc = Path.objects.filter(pk=be.pk)[0]
        ce = Path.objects.filter(name="BE").exclude(pk=be.pk)[0]
        self.assertEqual(len(bc.aggregations.all()), 1)
        self.assertEqual(len(ce.aggregations.all()), 1)
        aggr_bc = bc.aggregations.all()[0]
        aggr_ce = ce.aggregations.all()[0]
        self.assertEqual((0.0, 1.0), (aggr_bc.start_position, aggr_bc.end_position))
        self.assertEqual((0.0, 1.0), (aggr_ce.start_position, aggr_ce.end_position))
        topology.reload()
        self.assertEqual(len(topology.aggregations.all()), 4)
        # Geometry has changed
        self.assertNotEqual(topology.geom, topogeom)
        # But extremities are equal
        self.assertEqual(topology.geom.coords[0], topogeom.coords[0])
        self.assertEqual(topology.geom.coords[-1], topogeom.coords[-1])

    def test_split_twice(self):
        """
        
             C   D
             +   +
             |   |
      A +--==+===+==--+ B
             |   |
             +---+ 
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.1, end=0.9)
        topogeom = topology.geom
        self.assertEqual(len(topology.paths.all()), 1)
        cd = PathFactory.create(name="CD", geom=LineString((1,2,0),(1,-2,0),
                                                           (3,-2,0),(3,2,0)))
        self.assertEqual(len(topology.paths.all()), 3)
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.4, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        ab3 = Path.objects.filter(name="AB").exclude(pk__in=[ab.pk,ab2.pk])[0]
        aggr_ab2 = ab2.aggregations.all()[0]
        aggr_ab3 = ab3.aggregations.all()[0]
        self.assertEqual((0.0, 1.0), (aggr_ab2.start_position, aggr_ab2.end_position))
        self.assertEqual((0.0, 0.6), (aggr_ab3.start_position, aggr_ab3.end_position))
        topology.reload()
        self.assertNotEqual(topology.geom, topogeom)
        self.assertEqual(topology.geom.coords[0], topogeom.coords[0])
        self.assertEqual(topology.geom.coords[-1], topogeom.coords[-1])

    def test_split_on_update(self):
        """                               + E
                                          :
                                         ||
        A +-----------+ B         A +----++---+ B
                                         ||
        C +-====-+ D              C +--===+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,-1,0),(4,-1,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.3, end=0.9)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((0,-1,0),(2,-1,0), (2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 2)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd = cd.aggregations.all()[0]
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((0.5, 1.0), (aggr_cd.start_position, aggr_cd.end_position))
        self.assertEqual((0.0, 0.75), (aggr_cd2.start_position, aggr_cd2.end_position))

    def test_split_on_update_2(self):
        """                               + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-==------+ D           C +--===+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,-1,0),(4,-1,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.15, end=0.3)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((0,-1,0),(2,-1,0), (2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((0.25, 0.5), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_3(self):
        """                               + E
                                          ||
                                          ||
        A +-----------+ B         A +-----+---+ B
                                          :
        C +------==-+ D           C +-----+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,-1,0),(4,-1,0)))
        # Create a topology
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.7, end=0.85)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((0,-1,0),(2,-1,0), (2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((0.25, 0.625), (aggr_cd2.start_position, aggr_cd2.end_position))



class SplitPathPointTopologyTest(TestCase):

    def test_split_tee_1(self):
        """
                C
        A +-----X----+ B
                |   
                +    AB exists with topology at C.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.5, end=0.5)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd = PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        
        self.assertEqual(len(topology.paths.all()), 3)
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual(len(cd.aggregations.all()), 1)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cb.start_position, aggr_cb.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_tee_2(self):
        """
                C
        A +--X--+----+ B
                |   
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.25, end=0.25)
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_ab.start_position, aggr_ab.end_position))

    def test_split_tee_3(self):
        """
                C
        A +-----+--X--+ B
                |   
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.75, end=0.75)
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 0)
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cb.start_position, aggr_cb.end_position))

    def test_split_tee_4(self):
        """
                C
        A X-----+----+ B
                |   
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=0.0, end=0.0)
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 0)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.0, 0.0), (aggr_ab.start_position, aggr_ab.end_position))

    def test_split_tee_5(self):
        """
                C
        A +-----+----X B
                |   
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(ab, start=1.0, end=1.0)
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2,0,0),(2,2,0)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 0)
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_cb.start_position, aggr_cb.end_position))


    def failing_test_split_on_update(self):
        """                               + E
                                          :
                                          :
        A +-----------+ B         A +-----X---+ B
                                          :
        C +---X---+ D              C +----+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.5, end=0.5)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,2,0))
        cd.save()
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 4)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(ab2.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        
        aggr_ab = ab.aggregations.all()[0]
        aggr_ab2 = ab2.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((1.0, 1.0), (aggr_ab2.start_position, aggr_ab2.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd2.start_position, aggr_cd2.end_position))


    def test_split_on_update_2(self):
        """                               + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-X-----+ D              C +--X-+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.25, end=0.25)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_3(self):
        """                               + E
                                          X
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-----X-+ D              C +----+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.75, end=0.75)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cd2.start_position, aggr_cd2.end_position))

    def test_split_on_update_4(self):
        """                               + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C X-------+ D              C X----+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=0.0, end=0.0)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_5(self):
        """                               X E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-------X D              C +----+ D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=1.0, end=1.0)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,2,0))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_cd2.start_position, aggr_cd2.end_position))

    def failing_test_split_on_update_6(self):
        """
                                          D
        A +-----------+ B         A +-----X---+ B
                                          :
        C +-------X D                     :
                                          +
                                          C
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=1.0, end=1.0)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,-2,0),(2,0,0))
        cd.save()
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        self.assertEqual(len(topology.paths.all()), 3)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cb.start_position, aggr_cb.end_position))
        self.assertEqual((1.0, 1.0), (aggr_cd.start_position, aggr_cd.end_position))

    def failing_test_split_on_update_7(self):
        """
                                          C
        A +-----------+ B         A +-----X---+ B
                                          :
        C X-------+ D                     :
                                          + D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0,0,0),(4,0,0)))
        cd = PathFactory.create(name="CD", geom=LineString((0,1,0),(4,1,0)))
        topology = TopologyFactory.create(no_path=True)
        topology.add_path(cd, start=1.0, end=1.0)
        self.assertEqual(len(topology.paths.all()), 1)
        
        cd.geom = LineString((2,0,0),(2,-2,0))
        cd.save()
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        self.assertEqual(len(topology.paths.all()), 3)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cb.start_position, aggr_cb.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))
